import logging

from src.API import annotations as ann
from src.API.api_config import templates
from src.API.functions import SecretFunc
from src.database import TokenManager

from fastapi import APIRouter
from fastapi import Request

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Profile"])


@router.get("/profile", tags=["Pages"])
async def profile_page(
    request: Request,
    user_lable: ann.user_lable,
    token_data: ann.check_user,
    db_session: ann.db_annotation,
):
    user_id = token_data["sub"]
    try:
        logger.info(f"Request for profile page {user_id=}")
        token_manager = TokenManager(db_session)
        token_record = await token_manager.get_token_by_user_id(user_id)
        if token_record is None:
            token_value = await SecretFunc.ensure_access_token(user_id, db_session)
            token_record = await token_manager.get_token_by_user_id(user_id) if token_value else None

        context = dict(user_lable)
        context["token"] = token_record.token if token_record else None

        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context=context,
        )
    except Exception:
        logger.error(
            f"Error when receiving the profile page {token_data=}",
            exc_info=True,
        )
        raise
