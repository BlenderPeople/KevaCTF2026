import datetime
import logging

from src import pydantic_models as pdm
from src.API import annotations as ann

from fastapi import APIRouter
from fastapi import HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Other"])


@router.post(
    "/send/support/message",
    status_code=200,
    tags=["Support"],
    summary="Sending a support request",
)
async def support_message(token_data: ann.check_user, req: pdm.SupportMessage):
    _ = req
    try:
        logger.info(f"Request to send a message to support {token_data=}")
        return {
            "status": f"{datetime.datetime.now()} INFO sqlalchemy.engine.Engine COMMIT"
        }

    except HTTPException:
        raise
    except Exception:
        logger.error(
            f"Error when processing sending a support request {token_data=}",
            exc_info=True,
        )
        raise
