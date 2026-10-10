from sqlalchemy import select
from sqlalchemy import update

import logging

from ..base_models import BaseDBM
from src.database.tables import User
from src import pydantic_models as pdm

logger = logging.getLogger(__name__)


class UserManager(BaseDBM):
    async def add_user(self, new_user: pdm.CrtUser) -> int:
        dict_user = new_user.model_dump()
        try:
            logger.info(f"Adding new user with {new_user.login=}")
            logger.debug(f"{dict_user=}")

            new_auth = User(**dict_user)
            self.db_session.add(new_auth)
            await self.db_session.flush()
            await self.db_session.refresh(new_auth)
            return new_auth.user_id
        except Exception:
            logger.error(f"Error adding user {new_user.login=}", exc_info=True)
            logger.debug(f"{dict_user}")
            await self.db_session.rollback()
            raise

    async def get_user(self, user_id: int) -> pdm.DBUser | None:
        try:
            logger.info(f"Fetching user by {user_id=}")
            result = await self.db_session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                logger.info(f"Not user found with {user_id=}")
                return None
            logger.info(f"Found user with {user_id=}")
            pdm_user = pdm.DBUser(**user.__dict__)
            logger.debug(f"{pdm_user.__dict__=}")
            return pdm_user
        except Exception:
            logger.error(f"Error fetching user by {user_id=}", exc_info=True)
            raise

    async def get_user_by_login(self, login: str) -> pdm.DBUser | None:
        try:
            logger.info(f"Fetching user by {login=}")
            result = await self.db_session.execute(
                select(User).where(User.login == login)
            )
            user = result.scalar_one_or_none()
            if user is None:
                logger.info(f"Not user found with {login=}")
                return None
            logger.info(f"Found user with {login=}")
            pdm_user = pdm.DBUser(**user.__dict__)
            logger.debug(f"{pdm_user.__dict__=}")
            return pdm_user
        except Exception:
            logger.error(f"Error fetching user by {login=}", exc_info=True)
            raise

    async def upd_user(self, user_id: int, upd_user: pdm.UpdUser) -> pdm.DBUser:
        unset_dict_user = upd_user.model_dump(exclude_defaults=True)
        try:
            logger.info(f"Updating user {user_id}")
            logger.debug(f"{unset_dict_user=}")

            result = await self.db_session.execute(
                update(User)
                .where(User.user_id == user_id)
                .values(**unset_dict_user)
                .returning(User)
            )

            updated_user = result.scalar_one_or_none()

            if updated_user is None:
                logger.warning(f"User {user_id} not found, nothing to update")
                await self.db_session.rollback()
                return None

            logger.info(f"User {user_id} updated successfully")
            return pdm.DBUser(**updated_user.__dict__)
        except Exception:
            logger.error(f"Failed to update user {user_id}", exc_info=True)
            await self.db_session.rollback()
            raise
