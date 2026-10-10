import logging

from fastapi import APIRouter, Depends, Request

from src.API import annotations as ann
from src.API.api_config import templates
from src.API.depends import AdminDepends

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Other"])


@router.get(
    "/relay/h4v3n/EchoOverr1de/adminGate9k3z",
    tags=["Pages"],
    dependencies=[Depends(AdminDepends.check_status_admin)],
)
async def admin_page(request: Request, user_lable: ann.user_lable):
    user_lable.update({"request": request})
    return templates.TemplateResponse("admin.html", user_lable)
