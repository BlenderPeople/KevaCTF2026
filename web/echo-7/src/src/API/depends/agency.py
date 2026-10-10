import logging
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException

from src.API import annotations as ann
from src.API.functions import JWTConfig
from src.database import UserManager

logger = logging.getLogger(__name__)


class AgencyDepends:
    @staticmethod
    async def get_token_data(access_token: Annotated[str, Cookie()]) -> dict[str, any]:
        try:
            logger.info("Dependence of jwt token decoding")
            token_data = JWTConfig.decode_jwt_token(access_token)
            return token_data
        except HTTPException:
            raise
        except Exception:
            logger.error(f"Error in jwt token decoding dependency {access_token=}", exc_info=True)
            raise

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
            if user is None or user.login != token_data["username"]:
                logger.info(f"There is no user with this {user_id=}")
                raise HTTPException(status_code=404, detail=f"There is no user with this {user_id=}")
            return token_data
        except HTTPException:
            raise
        except Exception:
            logger.error(f"Error when checking the existence of a user by {user_id=}", exc_info=True)
            raise


class OtherAgencyDepends:
    @staticmethod
    def get_user_lable(
        token_data: Annotated[str, Depends(AgencyDepends.check_existence_user_by_user_id)],
    ):
        return {"user": {"sub": token_data["username"], "status": token_data["status"]}}
