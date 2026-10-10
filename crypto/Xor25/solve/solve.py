import json
from typing import Any

def to_bytes(data: Any) -> bytes:
    """Преобразует любые данные в bytes."""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode("utf-8")
    # Для любых структур: dict, list, int, float, bool, None
    return json.dumps(data, ensure_ascii=False).encode("utf-8")

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR двух байтовых строк (повторяет ключ, если он короче)."""
    if len(b) == 0:
        raise ValueError("Второй аргумент не может быть пустым")
    return bytes([x ^ b[i % len(b)] for i, x in enumerate(a)])


def xor_any(a: Any, b: Any) -> bytes:
    """Универсальный XOR для любых типов данных."""
    ba = to_bytes(a)
    bb = to_bytes(b)
    return xor_bytes(ba, bb)

flag = "5b55444b5342544a734b55434b406e5a0144556e4601404c"

for i in range(0, 256):
    print(xor_any(bytes.fromhex(flag), i).decode())