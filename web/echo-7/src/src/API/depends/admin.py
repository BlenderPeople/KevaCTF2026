import logging
from typing import Annotated

from fastapi import Depends, HTTPException

from src.API.depends import AgencyDepends

logger = logging.getLogger(__name__)


class AdminDepends:
    @staticmethod
    def check_status_admin(
        token: Annotated[dict[str, any], Depends(AgencyDepends.get_token_data)],
    ) -> bool:
        try:
            logger.info(f"Checking the administrator's status {token=}")

            if token.get("status") != "Admin":
                logger.info(f"User status '{token.get('status')}' is not Admin")
                raise HTTPException(status_code=403, detail="Forbidden")
            return True
        except HTTPException:
            raise
        except Exception:
            logger.error(f"Error checking the administrator status {token=}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
