import pytest
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import UserManager
from src.database.managers.fixtures import db_session  # noqa
from src.database.managers.fixtures import drop_all  # noqa
from src.database.managers.fixtures import user_model  # noqa
from src.database.managers.fixtures import user_id  # noqa
from src import pydantic_models as pdm


@pytest.mark.anyio
@pytest.mark.parametrize(
    "login, hash_password",
    [("pivan123", "password123"), ("asldjlkasdjf12340zvlkasdvasdi1", "password123")],
)
async def test_add_user(
    login: str,
    hash_password: str,
    db_session: AsyncSession,  # noqa
):
    manager = UserManager(db_session)
    user_pd_model = pdm.CrtUser(login=login, hash_password=hash_password)
    user_id_db = await manager.add_user(new_user=user_pd_model)
    assert isinstance(user_id_db, int)


@pytest.mark.anyio
async def test_get_user(
    user_id: int,  # noqa
    user_model: pdm.CrtUser,  # noqa
    db_session: AsyncSession,  # noqa
):
    manager = UserManager(db_session)
    user = await manager.get_user(user_id=user_id)

    assert isinstance(user, pdm.DBUser)
    assert user.user_id == user_id
    assert user.login == user_model.login
    assert user.hash_password == user_model.hash_password


@pytest.mark.anyio
async def test_get_user_by_login(
    user_id: int,  # noqa
    user_model: pdm.CrtUser,  # noqa
    db_session: AsyncSession,  # noqa
):
    manager = UserManager(db_session)
    user = await manager.get_user_by_login(login=user_model.login)

    assert isinstance(user, pdm.DBUser)
    assert user.user_id == user_id
    assert user.login == user_model.login
    assert user.hash_password == user_model.hash_password


@pytest.mark.anyio
@pytest.mark.parametrize(
    "login, hash_password",
    [
        ("pivan321", "password423"),
        ("asldjlkasdjf12340zvlkasdvasdi1", "password423"),
        (None, "password423"),
        ("pivan321", None),
    ],
)
async def test_upd_user(
    user_id: int,  # noqa
    user_model: pdm.CrtUser,  # noqa
    login: Optional[str],
    hash_password: Optional[str],
    db_session: AsyncSession,  # noqa
):
    manager = UserManager(db_session)
    user_pd_model = pdm.UpdUser(login=login, hash_password=hash_password)
    user = await manager.upd_user(user_id=user_id, upd_user=user_pd_model)

    assert isinstance(user, pdm.DBUser)
    assert user.user_id == user_id
    assert user.login == login if login is not None else user_model.login
    assert (
        user.hash_password == hash_password
        if hash_password is not None
        else user_model.hash_password
    )


@pytest.mark.anyio
@pytest.mark.parametrize("id", [123])
async def test_get_non_existent_user(
    id: int,
    db_session: AsyncSession,  # noqa
):
    user_manager = UserManager(db_session)
    is_none = await user_manager.get_user(user_id=id)
    assert is_none is None


@pytest.mark.anyio
@pytest.mark.parametrize("id", [123])
async def test_upd_non_existent_user(
    id: int,
    user_model: pdm.CrtUser,  # noqa
    db_session: AsyncSession,  # noqa
):
    user_manager = UserManager(db_session)
    upd_user = pdm.UpdUser(**user_model.model_dump())
    is_none = await user_manager.upd_user(user_id=id, upd_user=upd_user)
    assert is_none is None
