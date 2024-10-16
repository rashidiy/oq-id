import os
from contextlib import asynccontextmanager
from dataclasses import dataclass

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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
