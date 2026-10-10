import logging
from typing import Annotated
from pydantic import ValidationError

from src import pydantic_models as pdm
from src.API import annotations as ann
from src.API.functions import HashPassword
from src.database import UserManager

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

logger = logging.getLogger(__name__)


class UserAuthDepends:
    async def check_uniqueness_user_login(
        username: ann.field, db_session: ann.db_annotation
    ) -> bool:
        try:
            logger.info(f"Starting the user {username=} uniqueness check dependency")
            user_manager = UserManager(db_session=db_session)

            user = await user_manager.get_user_by_login(username)
            if user:
                logger.info(f"The user with the {username=} already exists")
                raise HTTPException(
                    status_code=409,
                    detail=f"The user with the {username=} already exists",
                )
            return True
        except HTTPException:
            raise
        except Exception:
            logger.error(
                f"Error checking user {username=} for uniqueness", exc_info=True
            )
            raise

    async def check_existence_user_by_login(
        username: ann.field, password: ann.field, db_session: ann.db_annotation
    ) -> pdm.DBUser:
        _ = password
        try:
            logger.info(f"Start of user existence check by {username=}")
            user_manager = UserManager(db_session=db_session)

            user = await user_manager.get_user_by_login(username)
            if not user:
                logger.info(f"User with {username=} not found")
                raise HTTPException(
                    status_code=404, detail=f"User with {username=} not found"
                )
            logger.info(f"The user with the {username=} already exists")
            return user
        except HTTPException:
            raise
        except Exception:
            logger.error(
                f"Error when verifying the user's existence {username=}", exc_info=True
            )
            raise


class UserAuthDependsNoneAnswer:
    async def verify_password(
        cred_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user: Annotated[
            pdm.DBUser, Depends(UserAuthDepends.check_existence_user_by_login)
        ],
    ) -> tuple[int, str]:
        try:
            logger.info(
                f"User password verification dependency with {cred_data.username=}"
            )

            hash_password_db = user.hash_password

            status_verify = HashPassword.verify_password(
                cred_data.password, hash_password_db
            )
            if status_verify is False:
                logger.info(f"The password for user {cred_data.username=} is incorrect")
                raise HTTPException(
                    status_code=401,
                    detail=f"The password for user {cred_data.username=} is incorrect",
                    headers={"WWW-Authenticate": "Bearer", "type-error": "password"},
                )
            return (user.user_id, user.login)
        except HTTPException:
            raise
        except Exception:
            logger.error(
                f"Error in dependency when checking a user's password with a {cred_data.username=}",
                exc_info=True,
            )
            raise
