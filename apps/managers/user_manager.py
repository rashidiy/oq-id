from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from starlette import status

from db import BaseManager
from settings.config import conf
from utils.translations import trans as _

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

http_bearer = HTTPBearer()


class UserManager(BaseManager):
    """Handles user-related operations such as registration and authentication."""

    @classmethod
    async def user_exists(cls, phone_number: str) -> bool:
        """Checks if a user with the given phone number already exists."""
        async with cls._get_session() as session:
            existing_user = await session.scalar(select(cls).filter_by(phone_number=phone_number))
            return existing_user is not None

    @classmethod
    async def get_user_by_phone_number(cls, phone_number: str):
        """Fetches a user by their phone number."""
        async with cls._get_session() as session:
            result = await session.execute(select(cls).where(cls.phone_number == phone_number))
            return result.scalar_one_or_none()

    @classmethod
    async def create_user(cls, phone_number: str, password: str):
        """Creates a new user and stores them in the db."""
        async with cls._get_session() as session:
            new_user = cls(phone_number=phone_number, password_hash=cls.hash_password(password))
            session.add(new_user)
            await session.commit()
            return new_user

    @classmethod
    async def update_user(cls, user) -> None:
        """Updates the user in the database."""
        async with cls._get_session() as session:
            await session.merge(user)
            await session.commit()

    @classmethod
    async def current(cls, credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
        token = credentials.credentials
        try:
            payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[conf.JWT_ALGORITHM])
            return await cls.get(phone_number=payload.get('sub'))
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=_("Could not validate credentials"),
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)
