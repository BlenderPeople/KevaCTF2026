import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from uvicorn import run

from src import API
from src.database import create_tables
from src.log import config

logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Start of the Secret app")
    logger.info("Creating database tables")
    await create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Secret",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    logger.info("App initialized")

    # include routers
    app.include_router(API.auth_router)
    app.include_router(API.secret_router)
    app.include_router(API.support_router)
    app.include_router(API.settings_router)
    app.include_router(API.message_router)
    app.include_router(API.profile_router)

    logger.info("Routers connected")

    return app


app = create_app()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def handle_401_redirect(request: Request, call_next):
    response = await call_next(request)

    if response.status_code == 401:
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header or "*/*" in accept_header:
            if not request.url.path.startswith(("/login", "/register", "/static", "/logout")):
                logger.info(f"401 error on {request.url.path}, redirecting to /login")
                return RedirectResponse(url="/login")

    return response


@app.middleware("http")
async def handle_422_redirect(request: Request, call_next):
    response = await call_next(request)

    if response.status_code == 422:
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header or "*/*" in accept_header:
            if not request.url.path.startswith(("/login", "/register", "/static", "/logout")):
                logger.info(f"422 error on {request.url.path}, redirecting to /login")
                return RedirectResponse(url="/login")

    return response


@app.middleware("http")
async def handle_not_found(request: Request, call_next):
    response: Response = await call_next(request)

    if response.status_code in (302, 301, 303, 307, 308):
        return response

    if request.url.path in ("/favicon.ico", "/static", "/login", "/register", "/logout"):
        return response

    if request.method != "GET" and request.url.path in ("/login", "/register"):
        return response

    if response.status_code == 404 and response.headers.get("skip") is None:
        return RedirectResponse(url="/", status_code=302)

    return response


if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=57778)
