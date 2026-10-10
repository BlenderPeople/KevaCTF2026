import logging
import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src import pydantic_models as pdm
from src.API import annotations as ann
from src.API.api_config import templates
from src.API.depends import UserAuthDepends, UserAuthDependsNoneAnswer
from src.API.functions import HashPassword, JWTConfig
from src.configurations import main_config as mc
from src.database import UserManager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/login", tags=["Pages"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", tags=["Pages"])
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post(
    "/register",
    status_code=302,
    tags=["Auth"],
    summary="Registering a new user",
    dependencies=[Depends(UserAuthDepends.check_uniqueness_user_login)],
)
async def register_endpoint(
    username: ann.login_field,
    password: ann.password_field,
    db_session: ann.db_annotation,
):
    _ = pdm.PageCrtUser(login=username, password=password)
    try:
        logger.info(f"Request to register a new user {username=}")

        manager = UserManager(db_session)
        hash_password = HashPassword.hash_password(password)
        crt_user = pdm.CrtUser(login=username, hash_password=hash_password)

        await manager.add_user(crt_user)
        await db_session.commit()

        logger.info("The user has been successfully registered")
        return RedirectResponse(url="/login", status_code=302)

    except HTTPException:
        raise
    except Exception:
        logger.error(f"Error when registering a new user {username=}", exc_info=True)
        raise


@router.post("/login", status_code=200, tags=["Auth"], summary="User authorization")
async def login_endpoint(
    user_data: Annotated[tuple[int, str], Depends(UserAuthDependsNoneAnswer.verify_password)],
):
    user_id, login = user_data
    try:
        logger.info(f"Login attempt for {user_id=}")

        status = "User" if login != "admin" else mc.flag
        data = {"sub": user_id, "username": login, "status": status}
        token = JWTConfig.generate_jwt_token(data)

        response = JSONResponse({"access_token": token, "token_type": "bearer"})
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=mc.jwt_conf.expire * 60,
            samesite="strict",
        )

        logger.info(f"User with {user_id=} is authorized")
        return response
    except Exception:
        logger.error(f"Error authorizing user with {user_id=}")
        raise


@router.get("/logout", status_code=302, tags=["Auth"], summary="User logout")
async def logout_endpoint(request: Request):
    try:
        logger.info("Request to log out of your account /logout")
        redirect = RedirectResponse("/login", status_code=302)
        redirect.delete_cookie(key="access_token", httponly=True, samesite="strict")
        return redirect
    except Exception:
        logger.error("Error when logging out of your account on /logout", exc_info=True)
        raise
