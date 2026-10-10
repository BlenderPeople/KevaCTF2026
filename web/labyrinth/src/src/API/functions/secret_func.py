import logging
import secrets

from src.database import UserManager
from src.database import TokenManager
from src import pydantic_models as pdm

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class SecretFunc:
    @staticmethod
    async def check_uniqueness_user_login(login: str, db_session: AsyncSession) -> bool:
        try:
            logger.info(f"Starting the user {login=} uniqueness check dependency")
            user_manager = UserManager(db_session=db_session)

            user = await user_manager.get_user_by_login(login)
            if user:
                logger.info(f"The user with the {login=} already exists")
                raise HTTPException(
                    status_code=409, detail=f"The user with the {login=} already exists"
                )
            return True
        except HTTPException:
            raise
        except Exception:
            logger.error(f"Error checking user {login=} for uniqueness", exc_info=True)
            raise

    @staticmethod
    async def ensure_access_token(user_id: int, db_session: AsyncSession) -> str | None:
        try:
            token_manager = TokenManager(db_session=db_session)
            token_record = await token_manager.get_token_by_user_id(user_id)
            if token_record is not None:
                return token_record.token

            user_manager = UserManager(db_session=db_session)
            user = await user_manager.get_user(user_id)
            if user is None:
                logger.info(f"Cannot create access token because user with {user_id=} was not found")
                return None

            while True:
                token_value = secrets.token_hex(32)
                existing_token = await token_manager.get_token_by_value(token_value)
                if existing_token is None:
                    break

            await token_manager.add_token(
                pdm.Token(user_id=user_id, token=token_value)
            )
            await db_session.commit()
            return token_value
        except Exception:
            logger.error(f"Error ensuring access token for {user_id=}", exc_info=True)
            raise
