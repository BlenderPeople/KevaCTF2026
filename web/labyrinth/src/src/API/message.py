import httpx
import logging

from fastapi import HTTPException
from fastapi import Request
from fastapi import APIRouter
from fastapi import Depends

from src.API import annotations as ann
from src.API.depends import SecretDepends
from src.API.api_config import templates
from src.configurations import main_config
from src.database import UserManager
from src import pydantic_models as pdm 

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Message"])

@router.get("/message", tags=["Pages"])
async def message_page(
    request: Request,
    user_lable: ann.user_lable,
):
    context = dict(user_lable)
    context["send_token_url"] = main_config.app_conf.send_token_url
    return templates.TemplateResponse(
        request=request,
        name="message.html",
        context=context,
    )

@router.post(
    "/send-token",
    status_code=200,
    tags=["Message"],
    summary="Отправить свой токен доступа другому пользователю",
    dependencies=[Depends(SecretDepends.check_existence_user_by_user_id)]
    )
async def send_token(
    send: pdm.Send,
    db_session: ann.db_annotation):
    user_manager = UserManager(db_session)
    user = await user_manager.get_user_by_login(send.login)

    if not user:
        logger.info(f"There is no user with login={send.login}")
        raise HTTPException(
            status_code=404, detail=f"User with {send.login=} not found"
        )
    logger.info(f"User {user.user_id=} found")

    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                send.url,
                json={
                    "user_id": user.user_id,
                    "token": send.token
                }
            )
        except httpx.RequestError:
            pass

    return {"status": "The token was successfully sent"}
