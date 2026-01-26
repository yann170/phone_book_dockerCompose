from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi_users_db_sqlmodel import SQLModelUserDatabaseAsync  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import os
from dotenv import load_dotenv
from apps.models.models import User
from sqlmodel import SQLModel
from sqlmodel import Field


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Session async
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# Dépôt utilisateur pour FastAPI Users
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLModelUserDatabaseAsync(session, User)
