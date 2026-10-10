import random
import os

def xor_bytes(data: bytes, key: bytes) -> bytes:
    out = bytearray()
    k = len(key)
    for i, b in enumerate(data):
        out.append(b ^ key[i % k])
    return bytes(out)

def xor_file(input_path: str, output_path: str, key: bytes):
    with open(input_path, "rb") as f:
        data = f.read()
    xored = xor_bytes(data, key)
    with open(output_path, "wb") as f:
        f.write(xored)

if __name__ == "__main__":
    key = os.urandom(16)
    xor_file("keys.png", "key_leak.txt", key)