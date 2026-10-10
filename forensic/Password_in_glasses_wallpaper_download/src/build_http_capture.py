#!/usr/bin/env python3
import argparse
import struct
import time
import zlib
from pathlib import Path


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) + data[i + 1]
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def mac(addr: str) -> bytes:
    return bytes(int(part, 16) for part in addr.split(":"))


def ip(addr: str) -> bytes:
    return bytes(int(part) for part in addr.split("."))


def build_ipv4(src_ip: str, dst_ip: str, payload_len: int, ident: int) -> bytes:
    ver_ihl = 0x45
    tos = 0
    total_len = 20 + payload_len
    flags_frag = 0x4000
    ttl = 64
    proto = 6
    header = struct.pack(
        "!BBHHHBBH4s4s",
        ver_ihl,
        tos,
        total_len,
        ident,
        flags_frag,
        ttl,
        proto,
        0,
        ip(src_ip),
        ip(dst_ip),
    )
    chksum = checksum(header)
    return struct.pack(
        "!BBHHHBBH4s4s",
        ver_ihl,
        tos,
        total_len,
        ident,
        flags_frag,
        ttl,
        proto,
        chksum,
        ip(src_ip),
        ip(dst_ip),
    )


def build_tcp(src_ip: str, dst_ip: str, sport: int, dport: int, seq: int, ack: int, flags: int, payload: bytes) -> bytes:
    data_offset = 5
    offset_flags = (data_offset << 12) | flags
    window = 64240
    header = struct.pack("!HHLLHHHH", sport, dport, seq, ack, offset_flags, window, 0, 0)
    pseudo = ip(src_ip) + ip(dst_ip) + struct.pack("!BBH", 0, 6, len(header) + len(payload))
    chksum = checksum(pseudo + header + payload)
    return struct.pack("!HHLLHHHH", sport, dport, seq, ack, offset_flags, window, chksum, 0)


def build_frame(src_mac: str, dst_mac: str, src_ip: str, dst_ip: str, sport: int, dport: int, seq: int, ack: int, flags: int, payload: bytes, ident: int) -> bytes:
    eth = mac(dst_mac) + mac(src_mac) + b"\x08\x00"
    tcp = build_tcp(src_ip, dst_ip, sport, dport, seq, ack, flags, payload)
    iphdr = build_ipv4(src_ip, dst_ip, len(tcp) + len(payload), ident)
    return eth + iphdr + tcp + payload


def chunk_bytes(data: bytes, size: int):
    for i in range(0, len(data), size):
        yield data[i:i + size]


def pcap_record(frame: bytes, ts: float) -> bytes:
    sec = int(ts)
    usec = int((ts - sec) * 1_000_000)
    return struct.pack("<IIII", sec, usec, len(frame), len(frame)) + frame


def insert_text_chunk(png_bytes: bytes, keyword: str, text: str) -> bytes:
    if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit("password.png is not a PNG")
    off = 8
    end = len(png_bytes)
    while off < len(png_bytes):
        ln = int.from_bytes(png_bytes[off:off + 4], "big")
        typ = png_bytes[off + 4:off + 8]
        if typ == b"IEND":
            end = off
            break
        off += 12 + ln
    chunk_data = keyword.encode() + b"\x00" + text.encode()
    chunk_type = b"tEXt"
    chunk = struct.pack(
        "!I4s",
        len(chunk_data),
        chunk_type,
    ) + chunk_data
    crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
    chunk += struct.pack("!I", crc)
    return png_bytes[:end] + chunk + png_bytes[end:]


def append_http_flow(input_pcap: Path, output_pcap: Path) -> None:
    base = input_pcap.read_bytes()
    if len(base) < 24:
        raise SystemExit("invalid pcap")

    client_mac = "02:11:22:33:44:55"
    server_mac = "b8:27:eb:dc:93:d0"
    client_ip = "192.168.100.102"
    server_ip = "192.168.100.111"
    sport = 49152
    dport = 80
    client_seq = 1000
    server_seq = 5000

    png_path = Path("src/password.png")
    png_body = insert_text_chunk(png_path.read_bytes(), "Comment", "kevactf{png_object_inside}")

    request = (
        b"GET /password.png HTTP/1.1\r\n"
        b"Host: 192.168.100.111\r\n"
        b"User-Agent: curl/8.0\r\n"
        b"Accept: */*\r\n"
        b"Connection: close\r\n\r\n"
    )
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: image/png\r\n"
        b"Content-Disposition: attachment; filename=\"password.png\"\r\n"
        + f"Content-Length: {len(png_body)}\r\n".encode()
        + b"Connection: close\r\n\r\n"
        + png_body
    )

    ts = time.time()
    packets = [
        build_frame(client_mac, server_mac, client_ip, server_ip, sport, dport, client_seq, 0, 0x02, b"", 0x1001),
        build_frame(server_mac, client_mac, server_ip, client_ip, dport, sport, server_seq, client_seq + 1, 0x12, b"", 0x1002),
        build_frame(client_mac, server_mac, client_ip, server_ip, sport, dport, client_seq + 1, server_seq + 1, 0x10, b"", 0x1003),
        build_frame(client_mac, server_mac, client_ip, server_ip, sport, dport, client_seq + 1, server_seq + 1, 0x18, request, 0x1004),
    ]

    response_seq = server_seq + 1
    request_ack = client_seq + 1 + len(request)
    for idx, chunk in enumerate(chunk_bytes(response, 1300), start=5):
        packets.append(
            build_frame(
                server_mac,
                client_mac,
                server_ip,
                client_ip,
                dport,
                sport,
                response_seq,
                request_ack,
                0x18,
                chunk,
                0x1000 + idx,
            )
        )
        response_seq += len(chunk)

    packets.append(
        build_frame(client_mac, server_mac, client_ip, server_ip, sport, dport, request_ack, response_seq, 0x10, b"", 0x1100)
    )

    with output_pcap.open("wb") as out:
        out.write(base)
        for i, frame in enumerate(packets):
            out.write(pcap_record(frame, ts + i * 0.01))


def main() -> None:
    parser = argparse.ArgumentParser(description="Append an HTTP password.png flow to an existing pcap")
    parser.add_argument("-i", "--input", required=True, type=Path, help="Base pcap")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output pcap")
    args = parser.parse_args()
    append_http_flow(args.input, args.output)


if __name__ == "__main__":
    main()
