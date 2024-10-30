import random

from settings.config import redis_client


class OTPManager:
    """Handles OTP generation, storage, and validation."""

    @classmethod
    async def generate_otp(cls) -> str:
        """Generates a random 5-digit OTP."""
        return str(random.randint(10000, 99999))

    @classmethod
    async def store_otp(cls, key: str, otp: str, action: str):
        """Stores OTP in Redis with an expiration time."""
        key = cls._build_key(key, action)
        await redis_client.setex(key, 90, otp)

    @classmethod
    async def get_otp(cls, key: str, action: str) -> str:
        """Retrieves OTP from Redis."""
        key = cls._build_key(key, action)
        return await redis_client.get(key)

    @classmethod
    async def delete_otp(cls, key: str, action: str):
        """Deletes the OTP from Redis after successful validation."""
        key = cls._build_key(key, action)
        await redis_client.delete(key)

    @classmethod
    def _build_key(cls, key: str, action: str) -> str:
        """Helper method to build Redis key for OTP."""
        return f"{action}_otp:{key}"
