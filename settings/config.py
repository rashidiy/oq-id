import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()


@dataclass
class DatabaseConfig:
    NAME: str = os.getenv('DB_NAME')
    USER: str = os.getenv('DB_USER')
    PASS: str = os.getenv('DB_PASS')
    HOST: str = os.getenv('DB_HOST')
    PORT: str = os.getenv('DB_PORT')

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"


@dataclass
class Config:
    db: DatabaseConfig = field(default_factory=DatabaseConfig)


conf = Config()
engine = create_async_engine(conf.db.db_url, echo=True, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # noqa


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
