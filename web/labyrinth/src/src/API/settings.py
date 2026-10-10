import logging

from src import pydantic_models as pdm
from src.API import annotations as ann
from src.API.depends import SecretDepends
from src.API.functions import HashPassword
from src.API.functions import SecretFunc
from src.API.api_config import templates
from src.configurations import main_config
from src.database import UserManager

from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends
from fastapi import HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Other"])


@router.get("/settings", tags=["Pages"])
async def settings_page(
    request: Request,
    user_lable: ann.user_lable,
):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context=user_lable,
    )


@router.put(
    "/upd/user",
    status_code=200,
    tags=["Settings"],
    summary="Update user data (login/password)",
    dependencies=[Depends(SecretDepends.check_existence_user_by_user_id)],
)
async def settings_endpoint(
    token_data: ann.check_user,
    db_session: ann.db_annotation,
    upd_data: pdm.PageUpdUser,
):
    login = upd_data.login
    new_password = upd_data.new_password
    try:
        logger.info(f"Request to update user data {token_data=}")

        # Запрет обновления данных для администратора
        if token_data["username"] == main_config.admin_conf.login or token_data["sub"] == main_config.admin_conf.user_id:
            raise HTTPException(status_code=403, detail="Изменение данных администратора запрещено.")

        user_manager = UserManager(db_session)

        if login is not None and login != token_data["username"]:
            _ = await SecretFunc.check_uniqueness_user_login(login, db_session)

        hash_password = (
            HashPassword.hash_password(new_password)
            if new_password is not None
            else None
        )
        upd_db_model = pdm.UpdUser(login=login, hash_password=hash_password)

        user_upd = await user_manager.upd_user(
            user_id=token_data["sub"], upd_user=upd_db_model
        )
        if user_upd is None:
            logger.info(f"Data update error {token_data=}")
            await db_session.rollback()
            raise HTTPException(status_code=500, detail="Data update error")
        await db_session.commit()
        logger.info(f"User data updated successfully {token_data=}")
        return {"status": "OK"}
    except HTTPException:
        raise
    except Exception:
        logger.error(f"Error updating user data {token_data=}", exc_info=True)
        raise
