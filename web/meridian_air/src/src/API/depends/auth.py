import logging
from typing import Annotated
from pydantic import ValidationError

from src.API import annotations as ann
from src.API.functions import HashPassword
from src.database import UserManager

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

logger = logging.getLogger(__name__)


class UserAuthDepends:
    async def check_uniqueness_user_login(
        username: ann.login_field, db_session: ann.db_annotation
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

class UserAuthDependsNoneAnswer:
    async def verify_password(
        cred_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db_session: ann.db_annotation
    ) -> tuple[int, str]:
        try:
            user_manager = UserManager(db_session=db_session)
            logger.info(
                f"User password verification dependency with {cred_data.username=}"
            )

            input_hash_password = HashPassword.hash_password(cred_data.password)
            user = await user_manager.get_user_sqli(
                login=cred_data.username,
                hash_password=input_hash_password
            )
            if user is None:
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
