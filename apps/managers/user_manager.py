from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy import select
from starlette import status

from db import BaseManager
from settings.config import conf
from utils.translations import trans as _

http_bearer = HTTPBearer()


class UserManager(BaseManager):
    """Handles user-related operations such as registration, authentication, and permissions."""

    @classmethod
    async def item_exists(cls, user_id: int, app_id: int) -> bool:
        from models import UserPermission
        """Checks if a permission for a specific user and app exists."""
        async with cls._get_session() as session:
            query = select(UserPermission).filter_by(user_id=user_id, app_id=app_id)
            return await session.scalar(query) is not None

    @classmethod
    async def get_by(cls, **kwargs):
        """Fetches an item by specified field values (like phone number, email, etc.)."""
        async with cls._get_session() as session:
            result = await session.execute(select(cls).filter_by(**kwargs))
            return result.scalar_one_or_none()

    @classmethod
    async def current(cls, credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
        """Gets the current authenticated user based on JWT."""
        token = credentials.credentials
        try:
            payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[conf.JWT_ALGORITHM])
            user = await cls.get_by(phone_number=payload.get('sub'))
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
        """Verifies that the current user is in developer mode."""
        user = await cls.current(credentials=credentials)
        if not user.developer_mode:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=_("Permission denied"),
            )
        return user
