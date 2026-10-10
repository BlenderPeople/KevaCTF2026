import socket

HOST = "138.16.152.96"
PORT = 64444
TIMEOUT = 5
MODES = {"SUM", "MAX", "SEL"}


def solve(text: str) -> int:
    sel_part = text.split("Селекторные байты (HEX):\n")[1]
    selected = [int(x, 16) for x in sel_part.split("\n")[0].split()]
    seq_part = text.split("Последовательность:\n")[1].split("Передай итоговый")[0]

    lines = [line.strip() for line in seq_part.splitlines() if line.strip()]
    mode_lines = [i for i, line in enumerate(lines) if line in MODES]
    selected_set = set(selected)

    r_SUM = r_MAX = r_SEL = 0

    for idx, mode_idx in enumerate(mode_lines):
        mode = lines[mode_idx]
        hex_start = mode_idx + 1
        hex_end = mode_lines[idx + 1] if idx + 1 < len(mode_lines) else len(lines)
        hex_blob = " ".join(lines[hex_start:hex_end])
        data = bytes.fromhex(hex_blob)

        j, n = 0, len(data)
        while j + 2 <= n:
            pkt_type = data[j]
            pkt_len = data[j + 1]
            j += 2
            if j + pkt_len > n:
                break
            
            if pkt_len == 0:
                payload = []
                psum = 0
            else:
                payload = data[j : j + pkt_len]
                j += pkt_len
                psum = sum(payload)

            plen = len(payload)

            if mode == "SUM":
                r_SUM += psum
            elif mode == "MAX" and plen > r_MAX:
                r_MAX = plen
            elif mode == "SEL" and pkt_type in selected_set:
                r_SEL += 1

    return r_SUM + r_MAX + r_SEL


def main() -> None:
    with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as sock:
        sock.settimeout(TIMEOUT)
        data = ""
        while "Передай итоговый контрольный индекс" not in data:
            chunk = sock.recv(65536).decode(errors="ignore")
            if not chunk:
                break
            data += chunk

        sock.sendall(f"{solve(data)}\n".encode())
        print(sock.recv(4096).decode(errors="ignore"), end="")


if __name__ == "__main__":
    main()
