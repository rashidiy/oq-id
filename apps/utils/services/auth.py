from fastapi import HTTPException, Request

from settings.config import limiter
from utils.services import OTPManager


class AuthService:
    """Service class to handle authentication logic."""

    @staticmethod
    @limiter.limit("1/90 seconds", error_message="Too many requests, please try again in 90 seconds.")
    async def send_verification_code(request: Request, phone_number: str, action: str):
        otp = await OTPManager.generate_otp()
        await OTPManager.store_otp(phone_number, otp, action)
        print(f"Generated OTP for {phone_number}: {otp}")
        # TODO: Implement OTP sending logic (SMS, Email, etc.)
        return otp

    @staticmethod
    async def verify_otp(phone_number: str, otp: str, action: str):
        stored_otp = await OTPManager.get_otp(phone_number, action)
        if not stored_otp or stored_otp != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired.")
        await OTPManager.delete_otp(phone_number, action)
