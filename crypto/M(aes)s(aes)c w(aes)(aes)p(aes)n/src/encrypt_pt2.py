# aes_encrypt.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def aes_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plaintext, AES.block_size))

key = b'украли'
iv  = b'ваще всё украли'
plaintext = b'неизвестно'

ciphertext = aes_encrypt(plaintext, key, iv)

with open("cipher.bin", "wb") as f:
    f.write(ciphertext)
