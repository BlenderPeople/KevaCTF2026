import socket
import time

HOST = "138.16.152.96"
PORT = 62223
TIMEOUT = 6

def solve(text: str) -> int:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    res = 0
    i = 0 
    while (n := lines[i]) != "=== Stream ended ===":
        op1, oper, op2 = n.split()
        op1, op2 = int(op1), int(op2)
        if oper == "+":
            res += op1 + op2
        elif oper == "//":
            res += op1 // op2
        elif oper == "-":
            res += op1 - op2
        elif oper == "**":
            res += op1 ** op2
        elif oper == "*":
            res += op1 * op2
        i += 1
    return res
    

def main() -> None:
    with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as sock:
        sock.settimeout(TIMEOUT)
        data = ""
        while "=== Stream ended ===" not in data:
            chunk = sock.recv(1000).decode(errors="ignore")
            if not chunk:
                break
            data += chunk

        res = solve(data)
        sock.sendall(f"{res}\n".encode())
        time.sleep(1)
        print(sock.recv(65535).decode(errors="ignore").split("Correct!")[1].strip())


if __name__ == "__main__":
    main()
