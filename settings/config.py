import os
from dataclasses import dataclass

from redis.asyncio import Redis
from slowapi import Limiter
from slowapi.util import get_remote_address


@dataclass
class Config:
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')
    REDIS_HOST: str = os.getenv('REDIS_HOST')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT'))
    REDIS_DB: int = int(os.getenv('REDIS_DB'))
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD')


redis_client = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    password=Config.REDIS_PASSWORD,
    decode_responses=True
)

conf = Config()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}"
)
