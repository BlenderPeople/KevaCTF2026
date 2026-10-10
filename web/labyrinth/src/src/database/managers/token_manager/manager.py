from sqlalchemy import select
from sqlalchemy import delete

import logging

from ..base_models import BaseDBM
from src.database.tables import Token
from src import pydantic_models as pdm

logger = logging.getLogger(__name__)


class TokenManager(BaseDBM):
    async def add_token(self, token: pdm.Token) -> pdm.DBToken | None:
        dict_token = token.model_dump()
        try:
            logger.info(f"Adding new token for {token.user_id=}")
            logger.debug(f"{dict_token=}")

            new_token = Token(**dict_token)
            self.db_session.add(new_token)
            await self.db_session.flush()
            await self.db_session.refresh(new_token)
            return pdm.DBToken(**dict_token)
        except Exception:
            logger.error(f"Error adding token for {token.user_id=}", exc_info=True)
            logger.debug(f"{dict_token}")
            await self.db_session.rollback()
            raise

    async def get_token_by_user_id(self, user_id: int) -> pdm.DBToken | None:
        try:
            logger.info(f"Fetching token by {user_id=}")
            result = await self.db_session.execute(
                select(Token).where(Token.user_id == user_id)
            )
            token = result.scalar_one_or_none()
            if token is None:
                logger.info(f"Not token found with {user_id=}")
                return None
            logger.info(f"Found token with {user_id=}")
            return pdm.DBToken(**token.__dict__)
        except Exception:
            logger.error(f"Error fetching token by {user_id=}", exc_info=True)
            raise

    async def get_token_by_value(self, token_value: str) -> pdm.DBToken | None:
        try:
            logger.info("Fetching token by token value")
            result = await self.db_session.execute(
                select(Token).where(Token.token == token_value)
            )
            token = result.scalar_one_or_none()
            if token is None:
                logger.info("Token value not found")
                return None
            logger.info("Token value found")
            return pdm.DBToken(**token.__dict__)
        except Exception:
            logger.error("Error fetching token by token value", exc_info=True)
            raise
