import logging

from fastapi import APIRouter, Request

from src.API import annotations as ann
from src.API.api_config import templates

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Pages"])


@router.get("/agency", tags=["Pages"])
async def agency_page(request: Request, user_lable: ann.user_lable):
    user_lable.update({"request": request})
    return templates.TemplateResponse("agency.html", user_lable)


@router.get("/alerts", tags=["Pages"])
async def alerts_page(request: Request, user_lable: ann.user_lable):
    user_lable.update({"request": request})
    return templates.TemplateResponse("alerts.html", user_lable)


@router.get("/support", tags=["Pages"])
async def support_page(request: Request, user_lable: ann.user_lable):
    user_lable.update({"request": request})
    return templates.TemplateResponse("support.html", user_lable)


@router.get("/settings", tags=["Pages"])
async def settings_page(request: Request, user_lable: ann.user_lable):
    user_lable.update({"request": request})
    return templates.TemplateResponse("settings.html", user_lable)
