import logging

from src.API.api_config import templates
from src.API import annotations as ann


from fastapi import APIRouter
from fastapi import Request

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Pages"])


@router.get("/agency", tags=["Pages"])
async def agency_page(
    request: Request,
    user_lable: ann.user_lable,
):
    try:
        user_lable.update({"request": request})
        return templates.TemplateResponse("agency.html", user_lable)
    except Exception:
        logger.error("Error when sending the page /agency", exc_info=True)
        raise


@router.get("/alerts", tags=["Pages"])
async def alerts_page(
    request: Request,
    user_lable: ann.user_lable,
):
    user_lable.update({"request": request})
    return templates.TemplateResponse("alerts.html", user_lable)


@router.get("/support")
async def support_page(
    request: Request,
    user_lable: ann.user_lable,
):
    user_lable.update({"request": request})
    return templates.TemplateResponse("support.html", user_lable)


@router.get("/settings", tags=["Pages"])
async def settings_page(
    request: Request,
    user_lable: ann.user_lable,
):
    user_lable.update({"request": request})
    return templates.TemplateResponse("settings.html", user_lable)
