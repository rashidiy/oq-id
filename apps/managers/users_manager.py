from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.password import hash_password


class UserManager:
    """Handles user-related operations such as registration and authentication."""

    @classmethod
    async def user_exists(cls, phone_number: str, db: AsyncSession) -> bool:
        """Checks if a user with the given phone number already exists."""
        existing_user = await db.scalar(select(cls).filter_by(phone_number=phone_number))
        return existing_user is not None

    @classmethod
    async def get_user_by_phone_number(cls, db: AsyncSession, phone_number: str):
        """Fetches a user by their phone number."""
        result = await db.execute(select(cls).where(cls.phone_number == phone_number))
        return result.scalar_one_or_none()

    @classmethod
    async def create_user(cls, phone_number: str, password: str, db: AsyncSession):
        """Creates a new user and stores them in the database."""
        new_user = cls(phone_number=phone_number, password_hash=hash_password(password))
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
