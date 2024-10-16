from sqlalchemy import select

from db import BaseManager
from utils.password import hash_password


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
            new_user = cls(phone_number=phone_number, password_hash=hash_password(password))
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
