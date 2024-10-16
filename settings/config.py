import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker




@dataclass
class Config:
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15


redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

conf = Config()

