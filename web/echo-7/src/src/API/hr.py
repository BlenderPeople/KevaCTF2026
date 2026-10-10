import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from src import pydantic_models as pdm
from src.API import annotations as ann
from src.API.api_config import templates
from src.API.depends.hr import HRDepends
from src.database import HRManager
from src.jinja_funcs.ssti_sandbox import ssti_sandbox

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Other"])


@router.get("/add/hr", tags=["Pages"])
async def add_hr_page(request: Request, user_lable: ann.user_lable):
    user_lable.update({"request": request})
    return templates.TemplateResponse("add_hr.html", user_lable)


@router.get("/agents", tags=["Pages"])
async def agents_page(request: Request, user_lable: ann.user_lable):
    user_lable.update({"request": request})
    return templates.TemplateResponse("agents.html", user_lable)


@router.post("/add/hr", status_code=201, tags=["HR"], summary="Adding a new HR agent")
async def add_hr_endpoint(
    token_data: ann.check_user,
    db_session: ann.db_annotation,
    hr_model: pdm.PageCrtHR,
):
    dict_hr_model = hr_model.model_dump()
    try:
        logger.info(f"Request to add a new hr {dict_hr_model=}")

        organization = dict_hr_model.get("organization", "")
        dict_hr_model["organization"] = ssti_sandbox.render(organization)

        hr_manager = HRManager(db_session)
        db_crt_hr_model = pdm.CrtHR(**dict_hr_model, user_id=token_data["sub"])
        db_hr = await hr_manager.add_hr(db_crt_hr_model)
        await db_session.commit()
        return db_hr
    except Exception:
        logger.error(f"Error when creating a new hr agent {dict_hr_model}", exc_info=True)
        raise


@router.get("/get/all/hrs", status_code=200, tags=["HR"], summary="Retrieves all agents from the user")
async def get_all_hrs_user_endpoint(
    token_data: ann.check_user,
    db_session: ann.db_annotation,
):
    try:
        logger.info(f"Request to receive all agents {token_data['sub']=}")
        hr_manager = HRManager(db_session)
        all_hrs = await hr_manager.get_all_hr_by_user_id(token_data["sub"])

        if all_hrs is None:
            return []

        return [hr.model_dump() for hr in all_hrs]
    except Exception:
        logger.error(f"Error when receiving all agents {token_data['sub']=}", exc_info=True)
        raise


@router.delete(
    "/del/hr/{hr_id}",
    status_code=200,
    tags=["HR"],
    summary="Delete HR agent by ID",
    dependencies=[Depends(HRDepends.check_access_to_hr)],
)
async def del_hr_by_hr_id_endpoint(db_session: ann.db_annotation, hr_id: int):
    try:
        logger.info(f"Request to delete hr by {hr_id=}")
        hr_manager = HRManager(db_session)

        del_status = await hr_manager.del_hr_by_hr_id(hr_id)
        if del_status is None:
            logger.info(f"The HR with the specified {hr_id} does not exist")
            raise HTTPException(
                status_code=404, detail="HR not found", headers={"skip": "hr_not_found"}
            )
        await db_session.commit()
        return {"status": "OK"}
    except Exception:
        logger.error(f"Error when deleting hr by {hr_id}", exc_info=True)
        raise
