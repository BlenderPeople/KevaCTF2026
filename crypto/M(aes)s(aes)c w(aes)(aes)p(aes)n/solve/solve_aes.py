# aes_bruteforce_iv.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def brute_iv_raw(ciphertext: bytes, key: bytes, iv_prefix: bytes):
    assert len(iv_prefix) == 14

    for suffix in range(0, 2**16):
        iv = iv_prefix + suffix.to_bytes(2, "big")

        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = cipher.decrypt(ciphertext)

            # Пытаемся снять паддинг, но если не получается — просто выводим как есть
            try:
                pt_unpadded = unpad(pt, AES.block_size)
            except Exception:
                pt_unpadded = pt  # оставляем как есть

            print(f"IV: {iv.hex()}  PT: {pt_unpadded}")

        except Exception as e:
            # Даже ошибки можно игнорировать, но CBC обычно не падает
            print(f"IV: {iv.hex()}  ERROR: {e}")
            continue


if __name__ == "__main__":
    key = b"oops_im_broke_it"
    iv_prefix = b"\x00" * 14

    with open("cipher.bin", "rb") as f:
        ciphertext = f.read()

    brute_iv_raw(ciphertext, key, iv_prefix)