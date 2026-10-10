import logging

from src import pydantic_models as pdm
from src.API import annotations as ann
from src.API.depends import AgencyDepends
from src.API.functions import HashPassword
from src.API.functions import AgencyFunc
from src.database import UserManager

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Other"])


@router.put(
    "/upd/user",
    status_code=200,
    tags=["Settings"],
    summary="Update user data (login/password)",
    dependencies=[Depends(AgencyDepends.check_existence_user_by_user_id)],
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
        user_manager = UserManager(db_session)

        if login is not None and login != token_data["username"]:
            _ = await AgencyFunc.check_uniqueness_user_login(login, db_session)

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
