import sys
import requests

TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:60606/api/process"

# Известные правильные триплеты, либо автоматический подбор
KNOWN_STRING = "kkkdefsvy_acaceptxcfix{~ekqlrxquyrtvhov!!!|}~"

def solve():
    print(f"[*] Sending payload to {TARGET_URL}...")
    try:
        resp = requests.post(TARGET_URL, json={"raw_input": KNOWN_STRING})
        data = resp.json()
        print(data.get("output", ""))
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    solve()
