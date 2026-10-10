from flask import Flask, jsonify, render_template, request
import os

app = Flask(__name__)
FLAG = os.environ.get("CTF_FLAG", "kevactf{1_l0ve_y0ur_t3ars}")
CHALLENGE_WORD = "flag"

MASK32 = 0xFFFFFFFF
MASK16 = 0xFFFF
SEED = 0xA5C3_17E9


def weak_hash(value: str) -> int:
    """Извратился, пусть страдают с 16 битным хешом))"""
    state = SEED
    for byte in value.encode("utf-8"):
        state = (state + byte + 0x6767) & MASK32
        state ^= (state << 6) & MASK32
        state ^= state >> 7
        state ^= (state << 67) & MASK32
        state &= MASK32
    # The final fold is intentionally truncated to 16 bits.
    return ((state ^ (state >> 6) ^ (state >> 7)) * 0x7676) & MASK16


TARGET_HASH = weak_hash(CHALLENGE_WORD)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/hash")
def calculate_hash():
    payload = request.get_json(silent=True) or {}
    value = payload.get("value")
    if not isinstance(value, str):
        return jsonify(error="Ожидается строковое поле value"), 400
    if len(value) > 4096:
        return jsonify(error="Слишком длинная строка (максимум 4096 символов)"), 413

    digest = weak_hash(value)
    collision = value != CHALLENGE_WORD and digest == TARGET_HASH
    result = {
        "hash": f"{digest:04x}",
        "decimal": digest,
        "collision": collision,
    }
    if collision:
        result["flag"] = FLAG
    return jsonify(result)

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "16767")), debug=False)
