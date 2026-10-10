import re
import socket

HOST, PORT = "138.16.152.96", 55555
cycle = re.compile(r'1{3,5}10{4,10}10{3,12}')

def main():
    with socket.create_connection((HOST, PORT), timeout=2) as s:
        data = ""

        while "Max length:" not in data:
            try:
                chunk = s.recv(4096).decode()
                if not chunk:
                    break
                data += chunk
            except TimeoutError:
                break

        matches = list(cycle.finditer(data))

        longest = current = 0
        prev_end = -1

        for m in matches:
            if m.start() == prev_end:
                current += 1
            else:
                longest = max(longest, current)
                current = 1
            prev_end = m.end()

        longest = max(longest, current)

        s.sendall(f"{longest}\n".encode())

        try:
            resp = s.recv(4096).decode()
            print(resp.strip() if "keva" in resp else "не найден флаг")
        except TimeoutError:
            print("не найден флаг")

if __name__ == "__main__":
    main()