import random

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from settings.config import Config, redis_client
from utils.password import hash_password


class OTPManager:
    """Handles OTP generation, storage, and validation."""

    @staticmethod
    async def generate_otp() -> str:
        """Generates a random 5-digit OTP."""
        return str(random.randint(10000, 99999))

    @staticmethod
    async def store_otp(phone_number: str, otp: str, action: str):
        """Stores OTP in Redis with an expiration time."""
        key = OTPManager._build_key(phone_number, action)
        await redis_client.setex(key, Config.OTP_EXPIRATION_MINUTES * 60, otp)

    @staticmethod
    async def get_otp(phone_number: str, action: str) -> str:
        """Retrieves OTP from Redis."""
        key = OTPManager._build_key(phone_number, action)
        return await redis_client.get(key)

    @staticmethod
    async def delete_otp(phone_number: str, action: str):
        """Deletes the OTP from Redis after successful validation."""
        key = OTPManager._build_key(phone_number, action)
        await redis_client.delete(key)

    @staticmethod
    async def is_rate_limit_exceeded(phone_number: str, action: str) -> bool:
        """Checks if the OTP request rate limit is exceeded."""
        key = OTPManager._build_rate_limit_key(phone_number, action)
        request_count = await redis_client.get(key)

        if request_count and int(request_count) >= Config.OTP_REQUEST_LIMIT:
            expiration_time = await redis_client.ttl(key)
            return True, expiration_time
        return False, None

    @staticmethod
    async def increment_rate_limit(phone_number: str, action: str):
        """Increments the OTP request count with a rate limit."""
        key = OTPManager._build_rate_limit_key(phone_number, action)
        if not await redis_client.exists(key):
            await redis_client.set(key, 1, ex=Config.OTP_REQUEST_TIME_WINDOW)
        else:
            await redis_client.incr(key)

    @staticmethod
    def _build_key(phone_number: str, action: str) -> str:
        """Helper method to build Redis key for OTP."""
        return f"{action}_otp:{phone_number}"

    @staticmethod
    def _build_rate_limit_key(phone_number: str, action: str) -> str:
        """Helper method to build Redis key for rate limiting."""
        return f"{action}_rate_limit:{phone_number}"


class UserManager:
    """Handles user-related operations such as registration and authentication."""

    @staticmethod
    async def user_exists(phone_number: str, db: AsyncSession) -> bool:
        """Checks if a user with the given phone number already exists."""
        existing_user = await db.scalar(select(User).filter_by(phone_number=phone_number))
        return existing_user is not None

    @staticmethod
    async def get_user_by_phone_number(db: AsyncSession, phone_number: str) -> User | None:
        """Fetches a user by their phone number."""
        result = await db.execute(select(User).where(User.phone_number == phone_number))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(phone_number: str, password: str, db: AsyncSession) -> User:
        """Creates a new user and stores them in the database."""
        new_user = User(phone_number=phone_number, password_hash=hash_password(password))
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user


class AuthService:
    """Service class to handle authentication logic."""

    @staticmethod
    async def send_verification_code(phone_number: str, action: str):
        """Generates, stores, and sends OTP to the user, with rate limiting."""
        exceeded, remaining_time = await OTPManager.is_rate_limit_exceeded(phone_number, action)
        if exceeded:
            remaining_seconds = int(remaining_time) if remaining_time else 60
            raise HTTPException(
                status_code=429,
                detail=f"Too many OTP requests for {action}. Please try again in {remaining_seconds} seconds."
            )

        otp = await OTPManager.generate_otp()
        await OTPManager.store_otp(phone_number, otp, action)
        await OTPManager.increment_rate_limit(phone_number, action)
        # Sending Verification Code logic
        print(f"Generated OTP for {phone_number}: {otp}")

        return otp
    @staticmethod
    async def verify_otp(phone_number: str, otp: str, action: str):
        """Verifies the OTP for a specific action."""
        stored_otp = await OTPManager.get_otp(phone_number, action)
        if not stored_otp or stored_otp != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired.")
        await OTPManager.delete_otp(phone_number, action)
