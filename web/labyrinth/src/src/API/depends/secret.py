import logging
from typing import Annotated, Any

from fastapi import Cookie, Depends, HTTPException

from src.API import annotations as ann
from src.API.functions import JWTConfig
from src.configurations import main_config
from src.database import UserManager

logger = logging.getLogger(__name__)


class SecretDepends:
    @staticmethod
    async def get_token_data(access_token: Annotated[str, Cookie()] = None) -> dict[str, Any] | None:
        try:
            logger.info("Dependence of jwt token decoding")
            if not access_token:
                logger.info("No access_token cookie provided")
                raise HTTPException(status_code=401, detail="Not authenticated")
            token_data = JWTConfig.decode_jwt_token(access_token)
            return token_data
        except HTTPException:
            raise
        except Exception:
            logger.error(f"Error in jwt token decoding dependency {access_token=}", exc_info=True)
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    async def check_existence_user_by_user_id(
        token_data: Annotated[dict[str, any], Depends(get_token_data)],
        db_session: ann.db_annotation,
    ) -> dict[str, any]:
        user_id = token_data["sub"]
        try:
            logger.info(f"Start of user existence check by {user_id=}")
            user_manager = UserManager(db_session=db_session)

            user = await user_manager.get_user(user_id)
            if (
                (user is None or user.login != token_data["username"])
                and (token_data["sub"] != main_config.admin_conf.user_id or token_data["username"] != main_config.admin_conf.login)
            ):
                logger.info(f"There is no user with this {user_id=}")
                raise HTTPException(status_code=401, detail=f"There is no user with this {user_id=}")
            return token_data
        except HTTPException:
            raise
        except Exception:
            logger.error(f"Error when checking the existence of a user by {user_id=}", exc_info=True)
            raise


class OtherSecretDepends:
    @staticmethod
    def get_user_lable(
        token_data: Annotated[str, Depends(SecretDepends.check_existence_user_by_user_id)],
    ):
        return {"user": {"sub": token_data["username"], "status": token_data["status"]}}
