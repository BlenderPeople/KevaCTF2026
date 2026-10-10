import os
from flask import Flask, render_template, request, jsonify, send_from_directory, Response

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(BASE_DIR, 'notes')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hint')
def hint():
    filename = os.path.basename(request.args.get('file', 'hint.jpg'))
    
    # Fallback to hint.jpg if hint.png was requested but hint.jpg exists
    if filename == 'hint.png' and not os.path.exists(os.path.join(NOTES_DIR, 'hint.png')):
        filename = 'hint.jpg'
    
    try:
        return send_from_directory(NOTES_DIR, filename)
    except Exception:
        return Response("Document not found in archival records.", status=404, mimetype='text/plain')

# Secret target triplets: each triplet strictly averages to the corresponding letter of "kevactf{kruto!}"
TARGET_TRIPLETS = [
    "kkk",  # 0:  'k' (107) -> (107+107+107)/3 = 107
    "def",  # 1:  'e' (101) -> (100+101+102)/3 = 101
    "svy",  # 2:  'v' (118) -> (115+118+121)/3 = 118
    "_ac",  # 3:  'a' (97)  -> (95+97+99)/3    = 97
    "ace",  # 4:  'c' (99)  -> (97+99+101)/3   = 99
    "ptx",  # 5:  't' (116) -> (112+116+120)/3 = 116
    "cfi",  # 6:  'f' (102) -> (99+102+105)/3  = 102
    "x{~",  # 7:  '{' (123) -> (120+123+126)/3 = 123
    "ekq",  # 8:  'k' (107) -> (101+107+113)/3 = 107
    "lrx",  # 9:  'r' (114) -> (108+114+120)/3 = 114
    "quy",  # 10: 'u' (117) -> (113+117+121)/3 = 117
    "rtv",  # 11: 't' (116) -> (114+116+118)/3 = 116
    "hov",  # 12: 'o' (111) -> (104+111+118)/3 = 111
    "!!!",  # 13: '!' (33)  -> (33+33+33)/3    = 33
    "|}~"   # 14: '}' (125) -> (124+125+126)/3 = 125
]

FLAG = os.environ.get("FLAG", os.environ.get("CTF_FLAG", "kevactf{kruto!}"))

@app.route('/api/process', methods=['POST'])
def process_crypto():
    """
    Triplet verification oracle:
    Checks raw input chunked into 3-character segments against TARGET_TRIPLETS.
    Returns:
      - ✔     if all 3 characters in the triplet match their exact positions
      - [2/3] if 2 characters match
      - [1/3] if 1 character matches
      - ✖     if 0 characters match
    """
    data = request.get_json(force=True, silent=True) or {}
    raw_input = data.get('raw_input', '') or data.get('input', '')

    # Strip newlines / carriage returns that might be inserted during typing
    clean_raw = raw_input.replace('\r', '').replace('\n', '')

    # Chunk user raw input into 3-character triplets
    user_triplets = [clean_raw[i:i+3] for i in range(0, len(clean_raw), 3)]

    tape_results = []
    full_matches = 0

    for idx, target_trip in enumerate(TARGET_TRIPLETS):
        if idx < len(user_triplets):
            user_trip = user_triplets[idx]
            # Match characters (case-insensitive for alphabet letters)
            matches_in_trip = 0
            for c_u, c_t in zip(user_trip, target_trip):
                if c_u == c_t or c_u.lower() == c_t.lower():
                    matches_in_trip += 1

            if matches_in_trip == 3:
                tape_results.append("✔")
                full_matches += 1
            elif matches_in_trip == 2:
                tape_results.append("[2/3]")
            elif matches_in_trip == 1:
                tape_results.append("[1/3]")
            else:
                tape_results.append("✖")
        else:
            tape_results.append("✖")

    all_matched = (full_matches == len(TARGET_TRIPLETS))
    tape_display = " ".join(tape_results)

    if all_matched:
        output_text = (
            f"[VERIFICATION TAPE]:\n{tape_display}\n\n"
            f"[SUCCESS]: ALL 15 MECHANICAL TRIPLETS AUTHENTICATED!\n"
            f"FLAG: {FLAG}"
        )
    else:
        output_text = (
            f"[VERIFICATION TAPE]:\n{tape_display}\n\n"
            f"[STATUS]: {full_matches}/{len(TARGET_TRIPLETS)} TRIPLETS FULLY UNLOCKED"
        )

    return jsonify({
        "status": "success",
        "output": output_text,
        "all_matched": all_matched,
        "full_matches": full_matches,
        "total": len(TARGET_TRIPLETS)
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 60606))
    app.run(host='0.0.0.0', port=port, debug=False)
