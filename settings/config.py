import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from redis.asyncio import Redis
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

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"


@dataclass
class Config:
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    OTP_EXPIRATION_MINUTES = 2
    OTP_REQUEST_LIMIT = 1
    OTP_REQUEST_TIME_WINDOW = 60
    OTP_REDIS_KEY_TEMPLATE = "otp:{phone_number}"
    RATE_LIMIT_REDIS_KEY_TEMPLATE = "otp_rate_limit:{phone_number}"


redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)


conf = Config()
engine = create_async_engine(conf.db.db_url, echo=True, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # noqa


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
