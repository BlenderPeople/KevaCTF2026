import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from src import pydantic_models as pdm
from src.database import UserManager
from src.configurations import main_config as mc
from src.database import create_test_tables, engine_test
from src.database import TestSessionLocal


@pytest.fixture
async def db_session():
    await create_test_tables()
    db_session: AsyncSession = TestSessionLocal()
    try:
        yield db_session
    finally:
        await db_session.close()


@pytest.fixture(autouse=True)
async def drop_all():
    async with engine_test.begin() as conn:
        await conn.run_sync(mc.db.base.metadata.drop_all)


@pytest.fixture
def user_model():
    return pdm.CrtUser(login="pivan123", hash_password="password123")


@pytest.fixture
async def user_id(user_model: pdm.CrtUser, db_session: AsyncSession):  # noqa
    user_manager = UserManager(db_session)

    return await user_manager.add_user(user_model)
