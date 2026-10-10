KEY_LEN = 16

KNOWN = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\r'
    b'IHDR'
)

PNG_SIG = b'\x89PNG\r\n\x1a\n'

def xor_decrypt(data, key):
    return bytes(
        data[i] ^ key[i % len(key)]
        for i in range(len(data))
    )


with open("key_leak.png", "rb") as f:
    data = f.read()

assert len(data) >= KEY_LEN

# --- восстановление ключа

key = bytes(
    data[i] ^ KNOWN[i]
    for i in range(KEY_LEN)
)

print("Recovered key:", key)
print("Hex:", key.hex())

# --- расшифровка всего файла

decrypted = xor_decrypt(data, key)

with open("decrypted.png", "wb") as f:
    f.write(decrypted)

# --- проверка

if decrypted.startswith(PNG_SIG):
    print("OK")
else:
    print("Заголовок не тот")

# aes_decrypt.py



