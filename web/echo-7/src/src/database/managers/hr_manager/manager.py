from sqlalchemy import select
from sqlalchemy import delete

import logging

from ..base_models import BaseDBM
from src.database.tables import HRAgency
from src import pydantic_models as pdm

logger = logging.getLogger(__name__)


class HRManager(BaseDBM):
    async def add_hr(self, new_hr: pdm.CrtHR) -> pdm.DBHR | None:
        dict_hr = new_hr.model_dump()
        try:
            logger.info(f"Adding new hr for {new_hr.user_id=}")
            logger.debug(f"{dict_hr=}")

            new_hr = HRAgency(**dict_hr)
            self.db_session.add(new_hr)
            await self.db_session.flush()
            await self.db_session.refresh(new_hr)
            return pdm.DBHR(**new_hr.__dict__)
        except Exception:
            logger.error(f"Error adding hr for {new_hr.user_id=}", exc_info=True)
            logger.debug(f"{dict_hr}")
            await self.db_session.rollback()
            raise

    async def get_all_hr_by_user_id(self, user_id: int) -> list[pdm.DBHR] | None:
        try:
            logger.info(f"Fetching all hr agents by {user_id=}")
            result = await self.db_session.execute(
                select(HRAgency).where(HRAgency.user_id == user_id)
            )
            hrs = result.scalars().all()
            if not len(hrs):
                logger.info(f"Not hr agents found with {user_id=}")
                return None
            logger.info(f"Found hr agents with {user_id=}")
            list_hr = [pdm.DBHR(**hr.__dict__) for hr in hrs]
            return list_hr
        except Exception:
            logger.error(f"Error fetching all hr agents by {user_id=}", exc_info=True)
            raise

    async def get_hr_by_hr_id(self, hr_id: int) -> pdm.DBHR | None:
        try:
            logger.info(f"Fetching hr agent by {hr_id=}")
            result = await self.db_session.execute(
                select(HRAgency).where(HRAgency.hr_id == hr_id)
            )
            hr = result.scalar_one_or_none()
            if hr is None:
                logger.info(f"Not hr agent found with {hr_id=}")
                return None
            logger.info(f"Found hr agent with {hr_id=}")
            return pdm.DBHR(**hr.__dict__)
        except Exception:
            logger.error(f"Error fetching hr agent by {hr_id=}", exc_info=True)
            raise

    async def del_hr_by_hr_id(self, hr_id: int) -> bool | None:
        try:
            logger.info(f"Deleting hr agent by {hr_id=}")
            result = await self.db_session.execute(
                delete(HRAgency).where(HRAgency.hr_id == hr_id)
            )
            if result.rowcount == 0:
                logger.info(f"Hr not found {hr_id=}")
                return None
            logger.info(f"Hr agent {hr_id=} deleted")
            return True
        except Exception:
            logger.error(f"Error deleting hr agent by {hr_id=}", exc_info=True)
            await self.db_session.rollback()
            raise
