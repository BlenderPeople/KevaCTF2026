import datetime
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import TokenManager
from src.database.managers.fixtures import db_session  # noqa
from src.database.managers.fixtures import drop_all  # noqa
from src.database.managers.fixtures import user_model  # noqa
from src.database.managers.fixtures import user_id  # noqa
from src import pydantic_models as pdm


@pytest.fixture
def token_model():
    return pdm.Token(
        user_id=1,
        token="a7f0b5e39482b43df131991ef24fa7c37403b2a8d9b136baaa214ddfffa21d00"
    )


@pytest.fixture
async def token_id(
    token_model: pdm.Token,
    user_id: int,  # noqa
    db_session: AsyncSession,  # noqa
):
    manager = TokenManager(db_session)
    token = await manager.add_token(token=token_model)
    return token


@pytest.mark.anyio
@pytest.mark.parametrize(
    "token",
    [
        "a7f0b5e39482b43df131991ef24fa7c37403b2a8d9b136baaa214ddfffa21d00",
        "709b11ff09206d2003b50e665d96d3d5bfa5a0eab53a3d46c679f174d82ab953",
        "fa8205dd8602a5a87baffc2402f0a620c47bcb25c0a1804d8199336fbc1fc818"
        
    ]
)
async def test_add_token(
    token: str, # noqa
    db_session: AsyncSession,  # noqa
    user_id_db: int = 1
):
    manager = TokenManager(db_session)
    token_data_pd = pdm.Token(
        user_id=user_id_db,
        token=token
    )
    token_db = await manager.add_token(token=token_data_pd)

    assert token_db.user_id == user_id_db
    assert token_db.token == token


@pytest.mark.anyio
async def test_get_token_by_user_id(
    token_id: pdm.Token,  # noqa
    db_session: AsyncSession,  # noqa
):
    manager = TokenManager(db_session)
    token = await manager.get_token_by_user_id(token_id.user_id)

    assert token is not None
    assert token.user_id == token_id.user_id
    assert token.token == token_id.token


@pytest.mark.anyio
@pytest.mark.parametrize("id", [123])
async def test_get_non_existent_token_with_user_id(
    id: int,
    db_session: AsyncSession,  # noqa
):
    manager = TokenManager(db_session)
    is_none = await manager.get_token_by_user_id(id)
    assert is_none is None