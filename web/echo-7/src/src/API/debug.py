import logging

from src.API.api_config import templates

from fastapi import APIRouter
from fastapi.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Other"])


@router.get("/debug", tags=["Pages"])
async def debug_page(request: Request):
    return templates.TemplateResponse("debug.html", {"request": request})
