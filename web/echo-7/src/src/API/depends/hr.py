import logging

from fastapi import HTTPException

from src.API import annotations as ann
from src.database import HRManager

logger = logging.getLogger(__name__)


class HRDepends:
    @staticmethod
    async def check_access_to_hr(
        token_data: ann.check_user,
        db_session: ann.db_annotation,
        hr_id: int,
    ) -> bool:
        try:
            logger.info(f"Dependency on checking user access to hr {hr_id}")
            hr_manager = HRManager(db_session)
            hr = await hr_manager.get_hr_by_hr_id(hr_id)

            if hr is None or hr.user_id != token_data["sub"]:
                logger.info(f"Access to this hr {hr_id=} is prohibited")
                raise HTTPException(status_code=403, detail="Access to this hr is prohibited")
            return True
        except HTTPException:
            raise
        except Exception:
            logger.error(f"Error checking hr {hr_id=} affiliation", exc_info=True)
            raise
