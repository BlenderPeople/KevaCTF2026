import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from threading import Lock
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

BASE_DIR = Path(__file__).resolve().parent
ATTACHMENTS_DIR = BASE_DIR / "chat_files" / "attachments"
DB_PATH = BASE_DIR / "data" / "clicker.sqlite3"
SID_COOKIE = "sid"

app = FastAPI(title="clicker_task")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

FLAG = os.getenv("FLAG", "kevactf{C0ngr4ts_YouVe_f1nally_W0n}")
LOG_ID = "LogID405"
CLICK_GOAL = 1_000_000_000
CLICKER_DECOY_FLAG = "kevactf{qwerty123}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("clicker")

METRIC_HTTP_REQUESTS = Counter(
    "clicker_http_requests_total",
    "Total HTTP requests seen by clicker_task",
    ["method", "path", "status"],
)
METRIC_CHAT_MESSAGES = Gauge("clicker_chat_messages", "Current number of chat messages")
METRIC_CLICK_REQUESTS = Counter("clicker_click_requests_total", "Accepted click requests")
METRIC_CHAT_POSTS = Counter("clicker_chat_posts_total", "Chat posts sent by users")
METRIC_FAKE_REWARD = Counter("clicker_fake_reward_hits_total", "Times the fake clicker reward was revealed")

click_lock = Lock()
message_lock = Lock()
session_clicks: dict[str, int] = {}

CLUE_MESSAGES = [
    {"author": "lena", "time": "2026-03-21 12:16", "text": "if support says flag endpoint fails, use request id from response."},
    {"author": "alex", "time": "2026-03-21 12:17", "text": "you mean LogID? yes, query logs by that id."},
    {"author": "dima", "time": "2026-03-21 13:05", "text": "grafana viewer creds live in monitoring.env."},
    {"author": "alex", "time": "2026-03-21 13:06", "text": "it is mounted at /app/config/monitoring.env in the web container."},
    {"author": "misha", "time": "2026-03-21 13:08", "text": "the file download helper still takes raw name input at /chat/file?name=<filename>."},
    {"author": "lena", "time": "2026-03-21 13:12", "text": "from attachments, ../../config/monitoring.env lands on the mounted env file."},
]

NOISE_MESSAGES = [
    {"author": "misha", "time": "2026-03-21 11:58", "text": "merged the css tweak, looks less broken now."},
    {"author": "alex", "time": "2026-03-21 12:01", "text": "can someone check the chat scroll on mobile?"},
    {"author": "dima", "time": "2026-03-21 12:03", "text": "the dashboard title still needs a shorter subtitle."},
    {"author": "lena", "time": "2026-03-21 12:05", "text": "i fixed the typo in the button label again."},
    {"author": "misha", "time": "2026-03-21 12:07", "text": "please keep the click animation subtle."},
    {"author": "alex", "time": "2026-03-21 12:09", "text": "the container starts fine after the last compose change."},
    {"author": "dima", "time": "2026-03-21 12:11", "text": "need to trim the attachment list before demo."},
    {"author": "lena", "time": "2026-03-21 12:13", "text": "the chat history is still too long for no reason."},
    {"author": "misha", "time": "2026-03-21 12:15", "text": "can we keep the main page simple this time?"},
    {"author": "alex", "time": "2026-03-21 12:18", "text": "logs are readable enough after the latest cleanup."},
    {"author": "dima", "time": "2026-03-21 12:22", "text": "Grafana panel order looks okay now."},
    {"author": "lena", "time": "2026-03-21 12:24", "text": "i moved the note about the file helper into chat."},
    {"author": "misha", "time": "2026-03-21 12:27", "text": "the viewer account should stay read-only."},
    {"author": "alex", "time": "2026-03-21 12:31", "text": "the web app is much quieter without the old noise stream."},
    {"author": "dima", "time": "2026-03-21 12:36", "text": "do we still need the old backup notes?"},
    {"author": "lena", "time": "2026-03-21 12:40", "text": "no, just keep the developer chatter short."},
    {"author": "misha", "time": "2026-03-21 12:44", "text": "attachment downloads should be obvious enough."},
    {"author": "alex", "time": "2026-03-21 12:48", "text": "the deployment note needs one more pass."},
    {"author": "dima", "time": "2026-03-21 12:52", "text": "searching logs by exact token is still the fastest path."},
    {"author": "lena", "time": "2026-03-21 12:56", "text": "let's leave the rest of the page boring."},
]

def now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def attachments_list() -> list[str]:
    return sorted(item.name for item in ATTACHMENTS_DIR.iterdir() if item.is_file())


def build_chat_history() -> list[dict[str, str]]:
    messages = list(NOISE_MESSAGES) + list(CLUE_MESSAGES)
    messages.sort(key=lambda item: item["time"])
    return messages


CHAT_MESSAGES = build_chat_history()


def db_connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with db_connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_clicks (
                sid TEXT PRIMARY KEY,
                clicks INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def get_remote_addr(request: Request) -> str:
    if request.client is None:
        return "-"
    return request.client.host


def get_or_create_sid(request: Request) -> tuple[str, bool]:
    sid = request.cookies.get(SID_COOKIE)
    if sid:
        return sid, False
    return uuid4().hex, True


def current_click_count(request: Request) -> int:
    sid = request.cookies.get(SID_COOKIE, "")
    if not sid:
        return 0
    return session_clicks.get(sid, 0)


def click_goal_reached(user_clicks: int) -> bool:
    return user_clicks >= CLICK_GOAL


def update_runtime_metrics() -> None:
    METRIC_CHAT_MESSAGES.set(len(CHAT_MESSAGES))


@app.on_event("startup")
async def startup_event() -> None:
    # Load session clicks from database
    with db_connect() as conn:
        rows = conn.execute("SELECT sid, clicks FROM session_clicks").fetchall()
        for row in rows:
            session_clicks[row["sid"]] = row["clicks"]
    update_runtime_metrics()

    # Keep a single useful log line for the intended Grafana path.
    logger.error("FLAG_LOOKUP_FAILED id=%s remote=%s flag=%s", LOG_ID, "build", FLAG)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    METRIC_HTTP_REQUESTS.labels(request.method, request.url.path, str(response.status_code)).inc()
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    update_runtime_metrics()
    your_clicks = current_click_count(request)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "your_clicks": your_clicks,
            "click_goal": CLICK_GOAL,
            "click_goal_display": f"{CLICK_GOAL:,}",
            "click_goal_reached": click_goal_reached(your_clicks),
            "clicker_decoy_flag": CLICKER_DECOY_FLAG,
        },
    )


@app.post("/api/click")
async def click(request: Request):
    sid, sid_created = get_or_create_sid(request)
    with click_lock:
        user_clicks = session_clicks.get(sid, 0) + 1
        session_clicks[sid] = user_clicks
        goal_reached = user_clicks >= CLICK_GOAL
        
        # Save to database for persistence
        with db_connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO session_clicks (sid, clicks, updated_at) VALUES (?, ?, ?)",
                (sid, user_clicks, now_ts())
            )
            conn.commit()
    
    METRIC_CLICK_REQUESTS.inc()
    if goal_reached:
        METRIC_FAKE_REWARD.inc()
    update_runtime_metrics()

    response = JSONResponse(
        {
            "your_clicks": user_clicks,
            "goal": CLICK_GOAL,
            "goal_reached": goal_reached,
            "reward": CLICKER_DECOY_FLAG if goal_reached else "",
        }
    )
    if sid_created:
        response.set_cookie(SID_COOKIE, sid, httponly=True, samesite="lax")
    return response


@app.get("/flag")
async def flag(request: Request):
    return PlainTextResponse(f"{{ERROR, Couldn't get the flag kevactf{{..., {LOG_ID}}}", status_code=500)


@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    with message_lock:
        all_messages = list(CHAT_MESSAGES)
    update_runtime_metrics()
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "messages": all_messages,
            "attachments": attachments_list(),
        },
    )


@app.post("/chat/message")
async def chat_message(
    request: Request,
    nickname: str = Form(default=""),
    message: str = Form(default=""),
):
    clean_nickname = nickname.strip()[:24]
    clean_message = message.strip()[:240]
    if not clean_nickname or not clean_message:
        return RedirectResponse(url="/chat", status_code=303)

    with message_lock:
        CHAT_MESSAGES.append({"author": clean_nickname, "time": now_ts(), "text": clean_message})

    METRIC_CHAT_POSTS.inc()
    update_runtime_metrics()
    return RedirectResponse(url="/chat", status_code=303)


@app.get("/chat/file")
async def chat_file(request: Request, name: str = ""):
    if not name:
        raise HTTPException(status_code=400, detail="filename is required")

    remote = get_remote_addr(request)
    allowed_attachments = set(attachments_list())
    special_env_alias = "../../config/monitoring.env"

    if name in allowed_attachments:
        requested_path = ATTACHMENTS_DIR / name
    elif name == special_env_alias:
        requested_path = BASE_DIR / "config" / "monitoring.env"
    else:
        logger.warning("PATH_TRAVERSAL_BLOCKED name=%s remote=%s", name, remote)
        raise HTTPException(status_code=403, detail="access denied")

    if not requested_path.is_file():
        logger.warning("FILE_READ_FAIL name=%s remote=%s", name, remote)
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path=requested_path)


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return "\n".join(
        [
            "User-agent: *",
            "Disallow: /flag",
            "Disallow: /chat",
        ]
    )


@app.get("/metrics")
async def metrics():
    update_runtime_metrics()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "ok"


init_db()
update_runtime_metrics()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, access_log=False)
