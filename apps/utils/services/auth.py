from fastapi import HTTPException

from utils.services import OTPManager


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
        # TODO Sending Verification Code logic
        print(f"Generated OTP for {phone_number}: {otp}")

        return otp

    @staticmethod
    async def verify_otp(phone_number: str, otp: str, action: str):
        """Verifies the OTP for a specific action."""
        stored_otp = await OTPManager.get_otp(phone_number, action)
        if not stored_otp or stored_otp != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired.")
        await OTPManager.delete_otp(phone_number, action)
