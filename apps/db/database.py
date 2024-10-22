import io
import os
import random
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps

from PIL import Image
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette import status

from utils.translations import trans as _

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

    @staticmethod
    def validate_fields(func):
        @wraps(func)
        async def wrapper(cls, **kwargs):
            for field_name in kwargs.keys():
                if not hasattr(cls, field_name):
                    raise ValueError(f"{field_name} is not a valid field of {cls.__name__}")
            return await func(cls, **kwargs)

        return wrapper

    @classmethod
    @validate_fields
    async def get(cls, **kwargs):
        """Fetches a object by its fields."""
        async with cls._get_session() as session:
            conditions = [getattr(cls, field_name) == field_value for field_name, field_value in kwargs.items()]
            query = select(cls).where(and_(*conditions))
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_obj_or_404(cls, **kwargs):
        obj = await cls.get(**kwargs)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_("Not found")
            )
        return obj

    @classmethod
    @validate_fields
    async def create(cls, **kwargs):
        """Creates a new object and stores in to the DB."""
        async with cls._get_session() as session:
            instance = cls(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    @classmethod
    async def update(cls, obj) -> None:
        """Updates the object in the database."""
        async with cls._get_session() as session:
            await session.merge(obj)
            await session.commit()

    @classmethod
    async def delete(cls, obj) -> None:
        async with cls._get_session() as session:
            await session.delete(obj)
            # result = await session.execute()
            await session.commit()

    @classmethod
    async def unordered_id(cls, from_=1000000000, to_=99999999999):
        async with cls._get_session() as session:
            while True:
                unique_id = random.randint(from_, to_)  # Generate 11-digit random number
                query = text(f"SELECT 1 FROM {cls.__tablename__} WHERE id = :id")
                result = await session.execute(query, {"id": unique_id})
                if not result.first():
                    return unique_id

    @staticmethod
    async def process_image(*, file: UploadFile, upload_file_path, width, height):
        try:
            image = Image.open(io.BytesIO(await file.read()))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file."
            )

        if image.format.lower() != 'png':
            image = image.convert('RGBA')

        if image.size != (width, height):
            image = image.resize((width, height))

        image.save(upload_file_path, format='PNG')

    def is_json_serializable(self, obj):
        if isinstance(obj, (str, int, float, bool, type(None))):
            return True

        elif isinstance(obj, (list, tuple)):
            return all(self.is_json_serializable(item) for item in obj)

        elif isinstance(obj, dict):
            return all(isinstance(key, str) and self.is_json_serializable(value) for key, value in obj.items())

        return False

    def to_dict(self, *fields: str):
        d = {}
        for field in fields:
            val = getattr(self, field)
            if val and not self.is_json_serializable(val):
                if getattr(val, '__str__'):
                    val = str(val)
                else:
                    continue
            d[field] = val
        return d
