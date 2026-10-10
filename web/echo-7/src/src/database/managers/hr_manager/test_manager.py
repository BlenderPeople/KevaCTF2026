import datetime
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import HRManager
from src.database.managers.fixtures import db_session  # noqa
from src.database.managers.fixtures import drop_all  # noqa
from src.database.managers.fixtures import user_model  # noqa
from src.database.managers.fixtures import user_id  # noqa
from src import pydantic_models as pdm


@pytest.fixture
def hr_model():
    return pdm.CrtHR(
        user_id=1,
        full_name="Имя Фамилия Отчество",
        age=12,
        position="Олег",
        organization="Организация",
        departament="Департамент",
        create_date=datetime.date.today(),
    )


@pytest.fixture
async def hr_id(
    hr_model: pdm.CrtHR,
    user_id: int,  # noqa
    db_session: AsyncSession,  # noqa
):
    manager = HRManager(db_session)
    hr = await manager.add_hr(new_hr=hr_model)
    return hr


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("user_id, full_name, age,position, organization, departament,create_date"),
    [
        (
            1,
            "иван иван иван",
            12,
            "должность",
            "организация",
            "departament",
            datetime.date.today(),
        ),
        (
            1,
            "т в",
            150,
            "должность",
            "организация",
            "departament",
            datetime.date.today(),
        ),
        (
            1,
            "Pivan",
            1,
            "должность",
            "organizatорганизацияion",
            "departament",
            datetime.date.today(),
        ),
    ],
)
async def test_add_hr(
    user_id: int,  # noqa
    full_name: str,
    age: int,
    position: str,
    organization: str,
    departament: str,
    create_date: datetime.date,
    db_session: AsyncSession,  # noqa
):
    manager = HRManager(db_session)
    crt_pd_model = pdm.CrtHR(
        user_id=user_id,
        full_name=full_name,
        age=age,
        position=position,
        organization=organization,
        departament=departament,
        create_date=create_date,
    )
    hr = await manager.add_hr(new_hr=crt_pd_model)

    assert hr.user_id == user_id
    assert hr.full_name == full_name
    assert hr.age == age
    assert hr.position == position
    assert hr.organization == organization
    assert hr.departament == departament
    assert hr.create_date == create_date


@pytest.mark.anyio
async def test_get_all_hr_by_user_id(
    hr_id: int,  # noqa
    hr_model: pdm.CrtHR,
    db_session: AsyncSession,  # noqa
):
    manager = HRManager(db_session)
    list_hr = await manager.get_all_hr_by_user_id(hr_model.user_id)

    assert len(list_hr) == 1
    assert list_hr[0].user_id == hr_model.user_id
    assert list_hr[0].full_name == hr_model.full_name
    assert list_hr[0].age == hr_model.age
    assert list_hr[0].position == hr_model.position
    assert list_hr[0].organization == hr_model.organization
    assert list_hr[0].departament == hr_model.departament
    assert list_hr[0].create_date == hr_model.create_date


@pytest.mark.anyio
async def test_get_hr_by_hr_id(
    hr_id: pdm.DBHR,  # noqa
    hr_model: pdm.CrtHR,
    db_session: AsyncSession,  # noqa
):
    manager = HRManager(db_session)
    hr = await manager.get_hr_by_hr_id(hr_id.hr_id)

    assert hr is not None
    assert hr.user_id == hr_model.user_id
    assert hr.full_name == hr_model.full_name
    assert hr.age == hr_model.age
    assert hr.position == hr_model.position
    assert hr.organization == hr_model.organization
    assert hr.departament == hr_model.departament
    assert hr.create_date == hr_model.create_date


@pytest.mark.anyio
async def test_del_hr_by_hr_id(
    hr_id: pdm.DBHR,  # noqa
    db_session: AsyncSession,  # noqa
):
    manager = HRManager(db_session)
    del_status = await manager.del_hr_by_hr_id(hr_id=hr_id.hr_id)

    assert del_status is True


@pytest.mark.anyio
@pytest.mark.parametrize("id", [123])
async def test_get_non_existent_list_hr_with_user_id(
    id: int,
    db_session: AsyncSession,  # noqa
):
    hr_manager = HRManager(db_session)
    is_none = await hr_manager.get_all_hr_by_user_id(user_id=id)
    assert is_none is None


@pytest.mark.anyio
@pytest.mark.parametrize("id", [123])
async def test_get_non_existent_hr_with_hr_id(
    id: int,
    db_session: AsyncSession,  # noqa
):
    hr_manager = HRManager(db_session)
    is_none = await hr_manager.get_hr_by_hr_id(id)
    assert is_none is None


@pytest.mark.anyio
@pytest.mark.parametrize("id", [123])
async def test_del_non_existent_user(
    id: int,
    db_session: AsyncSession,  # noqa
):
    hr_manager = HRManager(db_session)
    is_none = await hr_manager.del_hr_by_hr_id(hr_id=id)
    assert is_none is None
