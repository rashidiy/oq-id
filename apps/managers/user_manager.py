from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy import select
from starlette import status

from db import BaseManager
from managers import PassManager
from settings.config import conf
from utils.translations import trans as _

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
        return await cls.create(phone_number=phone_number, password_hash=PassManager.hash_password(password))

    @classmethod
    async def current(cls, credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
        token = credentials.credentials
        try:
            payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[conf.JWT_ALGORITHM])
            user = await cls.get(phone_number=payload.get('sub'))
            if user:
                return user
        except JWTError:
            pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_("Could not validate credentials"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    @classmethod
    async def developer(cls, credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
        user = await cls.current(credentials=credentials)
        if not user.developer_mode:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=_("Permission denied"),
            )
        return user
