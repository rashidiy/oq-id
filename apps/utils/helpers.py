import random

from fastapi import HTTPException
from models.users import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from settings.config import Config, redis_client


async def generate_otp() -> str:
    return str(random.randint(10000, 99999))


async def store_vc_to_redis(phone_number: str, otp: str, action: str):
    key = f"{action}_otp:{phone_number}"
    await redis_client.setex(key, Config.OTP_EXPIRATION_MINUTES * 60, otp)


async def get_vc_from_redis(phone_number: str, action: str) -> str:
    key = f"{action}_otp:{phone_number}"
    return await redis_client.get(key)


async def delete_vc_from_redis(phone_number: str, action: str):
    key = f"{action}_otp:{phone_number}"
    await redis_client.delete(key)


async def is_rate_limit_exceeded(phone_number: str, action: str) -> bool:
    key = f"{action}_rate_limit:{phone_number}"
    request_count = await redis_client.get(key)
    return request_count and int(request_count) >= Config.OTP_REQUEST_LIMIT


async def increment_rate_limit(phone_number: str, action: str):
    key = f"{action}_rate_limit:{phone_number}"
    if not await redis_client.exists(key):
        await redis_client.set(key, 1, ex=Config.OTP_REQUEST_TIME_WINDOW)
    else:
        await redis_client.incr(key)


async def user_exists(phone_number: str, db: AsyncSession) -> bool:
    existing_user = await db.scalar(select(User).filter_by(phone_number=phone_number))
    return existing_user is not None


async def get_user_by_phone_number(db: AsyncSession, phone_number: str) -> User | None:
    result = await db.execute(
        select(User).where(User.phone_number == phone_number)
    )
    return result.scalar_one_or_none()


async def send_verification_code(phone_number: str, action: str) -> str:
    if await is_rate_limit_exceeded(phone_number, action):
        raise HTTPException(status_code=429, detail=f"Too many OTP requests for {action}. Please try again later.")

    otp = await generate_otp()
    await store_vc_to_redis(phone_number, otp, action)
    await increment_rate_limit(phone_number, action)
    print(f"Generated OTP for {phone_number}: {otp}")
    return otp
