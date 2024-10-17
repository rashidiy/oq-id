import os
from contextlib import asynccontextmanager
from dataclasses import dataclass

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_

load_dotenv()


@dataclass
class DatabaseConfig:
    NAME: str = os.getenv('DB_NAME')
    USER: str = os.getenv('DB_USER')
    PASS: str = os.getenv('DB_PASS')
    HOST: str = os.getenv('DB_HOST')
    PORT: str = os.getenv('DB_PORT')

    @classmethod
    def url(cls):
        return f"postgresql+asyncpg://{cls.USER}:{cls.PASS}@{cls.HOST}:{cls.PORT}/{cls.NAME}"


class BaseManager:
    engine = create_async_engine(DatabaseConfig.url(), echo=True, future=True)
    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    @classmethod
    @asynccontextmanager
    async def _get_session(cls) -> AsyncSession:
        async with cls.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    @classmethod
    async def get(cls, **kwargs):
        """Fetches a user by their fields."""
        for field_name in kwargs.keys():
            if not hasattr(cls, field_name):
                raise ValueError(f"{field_name} is not a valid field of {cls.__name__}")

        async with cls._get_session() as session:
            conditions = [getattr(cls, field_name) == field_value for field_name, field_value in kwargs.items()]
            query = select(cls).where(and_(*conditions))
            result = await session.execute(query)
            return result.scalar_one_or_none()
