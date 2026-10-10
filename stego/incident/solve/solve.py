import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

DEFAULT_PNG = Path(__file__).resolve().parent.parent / "public" / "error.png"


def extract_zip_tail(png_path: str) -> bytes:
    data = open(png_path, "rb").read()
    pk_pos = data.find(b"PK\x03\x04")
    if pk_pos == -1:
        raise ValueError("No embedded ZIP found in the file")
    return data[pk_pos:]


def extract_lsb_text(img: Image.Image) -> str:
    pixels = list(img.convert("RGB").getdata())
    bits = []
    for r, g, b in pixels:
        bits.extend([r & 1, g & 1, b & 1])

    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for bit in bits[i:i + 8]:
            byte = (byte << 1) | bit
        if byte == 0:
            break
        chars.append(chr(byte))
    return "".join(chars)


def main() -> None:
    png_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_PNG)

    zip_bytes = extract_zip_tail(png_path)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        inner_name = archive.namelist()[0]
        inner_bytes = archive.read(inner_name)
    print(f"[+] Extracted '{inner_name}' from the ZIP appended to {png_path}")

    img = Image.open(io.BytesIO(inner_bytes))
    img.load()
    print(f"[+] Hint in PNG metadata: {img.text}")

    flag = extract_lsb_text(img)
    print(f"[+] Flag: {flag}")


if __name__ == "__main__":
    main()
