#!/usr/bin/env python3

import os
import struct
import zipfile
import zlib

from PIL import Image, ImageDraw, ImageFont

YOUR_PNG = "incident.png"
OUTPUT_FILE = "../public/error.png"

FULL_FLAG = "kevactf{N0_1nC1d3nt_C4n_H1d3_Fr0m_Y0u}"

CONTAINER_W = 640
CONTAINER_H = 120


def ensure_file_exists(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)


def create_container_image(text: str, output_file: str) -> None:
    img = Image.new("RGB", (CONTAINER_W, CONTAINER_H), color="#0a0a0a")
    draw = ImageDraw.Draw(img)

    try:
        font_main = ImageFont.truetype(
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", 24
        )
    except Exception:
        font_main = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font_main)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (CONTAINER_W - text_width) // 2
    y = (CONTAINER_H - text_height) // 2

    draw.text((x, y), text, fill="#ff0000", font=font_main)

    img.save(output_file, "PNG")


def embed_flag_in_lsb(image_file: str, flag: str, output_file: str) -> None:
    img = Image.open(image_file).convert("RGB")
    pixels = list(img.getdata())

    bits = []
    for ch in flag:
        c = ord(ch)
        for i in range(7, -1, -1):
            bits.append((c >> i) & 1)

    total_pixels = len(pixels)
    capacity = total_pixels * 3

    if len(bits) > capacity:
        raise ValueError(f"LSB overflow: need {len(bits)} bits, have {capacity}")

    bits += [0] * (capacity - len(bits))

    new_pixels = []
    idx = 0
    for r, g, b in pixels:
        r = (r & 0xFE) | bits[idx]
        idx += 1
        g = (g & 0xFE) | bits[idx]
        idx += 1
        b = (b & 0xFE) | bits[idx]
        idx += 1
        new_pixels.append((r, g, b))

    out = Image.new("RGB", img.size)
    out.putdata(new_pixels)
    out.save(output_file, "PNG")


def add_hidden_text_to_png(png_file: str) -> None:
    with open(png_file, "rb") as f:
        data = bytearray(f.read())

    hidden_text = "use zsteg"
    text_bytes = hidden_text.encode()

    tEXt_chunk = b"tEXt"
    keyword = b"Comment"
    chunk_payload = keyword + b"\x00" + text_bytes
    chunk_length = len(chunk_payload)
    chunk_crc = zlib.crc32(tEXt_chunk + chunk_payload) & 0xFFFFFFFF

    tEXt = struct.pack(">I", chunk_length) + tEXt_chunk + chunk_payload + struct.pack(">I", chunk_crc)

    iend_pos = data.find(b"IEND")
    if iend_pos != -1:
        insert_pos = iend_pos - 4  # step back over IEND's own 4-byte length field
        data = data[:insert_pos] + tEXt + data[insert_pos:]

    with open(png_file, "wb") as f:
        f.write(data)


def cleanup(files) -> None:
    for path in files:
        if os.path.exists(path):
            os.remove(path)


def main():
    ensure_file_exists(YOUR_PNG)

    create_container_image("What you are looking for is here!", "container.png")
    print("[+] Created container image with hint text")

    embed_flag_in_lsb("container.png", FULL_FLAG, "SYSTEM_BREACH_DETECTED.png")
    print("[+] Embedded full flag into LSB of container image")

    add_hidden_text_to_png("SYSTEM_BREACH_DETECTED.png")
    print("[+] Added hidden text 'use zsteg' to PNG metadata")

    with zipfile.ZipFile("archive.zip", "w") as z:
        z.write("SYSTEM_BREACH_DETECTED.png", "SYSTEM_BREACH_DETECTED.png")
    print("[+] Created ZIP archive with SYSTEM_BREACH_DETECTED.png inside")

    with open("archive.zip", "rb") as f:
        zip_data = f.read()

    with open(YOUR_PNG, "rb") as f:
        png_data = f.read()

    with open(OUTPUT_FILE, "wb") as f:
        f.write(png_data + zip_data)

    print(f"[+] Final file written: {OUTPUT_FILE}")

    cleanup([
        "container.png",
        "SYSTEM_BREACH_DETECTED.png",
        "archive.zip",
    ])


if __name__ == "__main__":
    main()