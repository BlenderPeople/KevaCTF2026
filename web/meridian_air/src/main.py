import logging
import logging.config
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from uvicorn import run

from src import API
from src.API.functions import HashPassword
from src.database import create_tables, SessionLocal
from src.database.tables import User
from src.log import config

logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


async def seed_admin_user() -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.login == "admin"))
        if result.scalar_one_or_none() is not None:
            logger.info("Admin user already exists, skipping seed")
            return

        password = secrets.token_urlsafe(32)
        session.add(User(login="admin", hash_password=HashPassword.hash_password(password)))
        await session.commit()
        logger.info(f"Created admin user with generated password: {password}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Start of the HR-Agency app")
    logger.info("Creating database tables")
    await create_tables()
    await seed_admin_user()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="HRAgency",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    logger.info("App initialized")

    app.include_router(API.auth_router)
    app.include_router(API.agency_router)
    app.include_router(API.support_router)
    app.include_router(API.settings_router)

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
            if not request.url.path.startswith(("/login", "/register", "/static")):
                logger.info(f"401 error on {request.url.path}, redirecting to /login")
                return RedirectResponse(url="/login")

    return response


@app.middleware("http")
async def handle_422_redirect(request: Request, call_next):
    response = await call_next(request)

    if response.status_code == 422:
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header or "*/*" in accept_header:
            if not request.url.path.startswith(("/login", "/register", "/static")):
                logger.info(f"422 error on {request.url.path}, redirecting to /login")
                return RedirectResponse(url="/login")

    return response


@app.middleware("http")
async def handle_not_found(request: Request, call_next):
    response: Response = await call_next(request)

    if response.status_code in (302, 301, 303, 307, 308):
        return response

    if request.method != "GET" and request.url.path in ("/login", "/register"):
        return response

    if request.url.path in ("/favicon.ico", "/static"):
        return response

    if response.status_code == 404 and response.headers.get("skip") is None:
        return RedirectResponse(url="/agency", status_code=302)

    return response


if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=57894)
