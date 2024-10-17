import os
from dataclasses import dataclass

from redis.asyncio import Redis


@dataclass
class Config:
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15


redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

conf = Config()
