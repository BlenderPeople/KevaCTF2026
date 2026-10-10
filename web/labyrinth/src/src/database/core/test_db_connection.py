from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.database.tables import User, Token  # noqa
from src.configurations import main_config as mc

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DB_URL, echo=True)
TestSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test
)


async def create_test_tables() -> None:
    async with engine_test.begin() as conn:
        await conn.run_sync(mc.db.base.metadata.create_all)
