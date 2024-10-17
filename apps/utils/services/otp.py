import random

from settings.config import redis_client


class OTPManager:
    """Handles OTP generation, storage, and validation."""
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    OTP_EXPIRATION_MINUTES = 2
    OTP_REQUEST_LIMIT = 1
    OTP_REQUEST_TIME_WINDOW = 60
    OTP_REDIS_KEY_TEMPLATE = "otp:{phone_number}"
    RATE_LIMIT_REDIS_KEY_TEMPLATE = "otp_rate_limit:{phone_number}"

    @classmethod
    async def generate_otp(cls) -> str:
        """Generates a random 5-digit OTP."""
        return str(random.randint(10000, 99999))

    @classmethod
    async def store_otp(cls, phone_number: str, otp: str, action: str):
        """Stores OTP in Redis with an expiration time."""
        key = cls._build_key(phone_number, action)
        await redis_client.setex(key, cls.OTP_EXPIRATION_MINUTES * 60, otp)

    @classmethod
    async def get_otp(cls, phone_number: str, action: str) -> str:
        """Retrieves OTP from Redis."""
        key = cls._build_key(phone_number, action)
        return await redis_client.get(key)

    @classmethod
    async def delete_otp(cls, phone_number: str, action: str):
        """Deletes the OTP from Redis after successful validation."""
        key = cls._build_key(phone_number, action)
        await redis_client.delete(key)

    @classmethod
    async def is_rate_limit_exceeded(cls, phone_number: str, action: str) -> tuple:
        """Checks if the OTP request rate limit is exceeded."""
        key = cls._build_rate_limit_key(phone_number, action)
        request_count = await redis_client.get(key)

        if request_count and int(request_count) >= cls.OTP_REQUEST_LIMIT:
            expiration_time = await redis_client.ttl(key)
            return True, expiration_time
        return False, None

    @classmethod
    async def increment_rate_limit(cls, phone_number: str, action: str):
        """Increments the OTP request count with a rate limit."""
        key = cls._build_rate_limit_key(phone_number, action)
        if not await redis_client.exists(key):
            await redis_client.set(key, 1, ex=cls.OTP_REQUEST_TIME_WINDOW)
        else:
            await redis_client.incr(key)

    @classmethod
    def _build_key(cls, phone_number: str, action: str) -> str:
        """Helper method to build Redis key for OTP."""
        return f"{action}_otp:{phone_number}"

    @classmethod
    def _build_rate_limit_key(cls, phone_number: str, action: str) -> str:
        """Helper method to build Redis key for rate limiting."""
        return f"{action}_rate_limit:{phone_number}"
