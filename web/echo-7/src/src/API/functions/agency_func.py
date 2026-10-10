import logging

from src.database import UserManager

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AgencyFunc:
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
