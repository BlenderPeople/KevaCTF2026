from typing import AsyncGenerator
import logging
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import pwdlib

from src.database.tables import User, Token  # noqa
from src.configurations import main_config

logger = logging.getLogger(__name__)
password_hash = pwdlib.PasswordHash.recommended()

engine: AsyncEngine = create_async_engine(main_config.db.db_url, echo=False)
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(main_config.db.base.metadata.create_all)
    await ensure_default_admin()


async def ensure_default_admin() -> None:
    async with SessionLocal() as db_session:
        try:
            admin_user_id = main_config.admin_conf.user_id
            admin_login = main_config.admin_conf.login
            admin_password = main_config.admin_conf.password

            admin_user = await db_session.get(User, admin_user_id)
            if admin_user is None:
                existing_admin = await db_session.execute(
                    select(User).where(User.login == admin_login)
                )
                existing_admin_user = existing_admin.scalar_one_or_none()
                if existing_admin_user is None:
                    admin_user = User(
                        user_id=admin_user_id,
                        login=admin_login,
                        hash_password=password_hash.hash(admin_password),
                    )
                    db_session.add(admin_user)
                    await db_session.flush()
                else:
                    logger.warning(
                        "Admin login already exists with unexpected user_id=%s; default admin seed skipped",
                        existing_admin_user.user_id,
                    )
                    await db_session.rollback()
                    return

            admin_user = await db_session.get(User, admin_user_id)
            if admin_user is None:
                await db_session.rollback()
                return

            admin_token = await db_session.execute(
                select(Token).where(Token.user_id == admin_user_id)
            )
            if admin_token.scalar_one_or_none() is None:
                while True:
                    token_value = secrets.token_hex(32)
                    existing_token = await db_session.execute(
                        select(Token).where(Token.token == token_value)
                    )
                    if existing_token.scalar_one_or_none() is None:
                        break
                db_session.add(Token(user_id=admin_user_id, token=token_value))

            await db_session.commit()
        except Exception:
            await db_session.rollback()
            logger.error("Failed to ensure default admin user", exc_info=True)
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db: AsyncSession = SessionLocal()
    try:
        logger.info("DataBase connection session has been created")
        yield db
    except Exception:
        logger.info("An error occurred while working with the session")
        await db.rollback()
        raise
    finally:
        logger.info("DataBase connection session has been closed")
        await db.close()
