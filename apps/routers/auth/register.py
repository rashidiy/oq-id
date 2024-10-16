from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from forms.auth_forms import (PreRegisterRequest,
                              RegisterRequest)
from models.users import User
from settings.config import Config, get_session
from utils.helpers import (OTPManager, AuthService)
from utils.jwt import create_access_token, create_refresh_token
from utils.translations import _  # noqa
from .base import router


@router.post("/pre_register", status_code=status.HTTP_200_OK)
async def pre_register(data: PreRegisterRequest, db: AsyncSession = Depends(get_session)):
    """
    Pre-register a new user by sending a verification code to their phone number.

    This endpoint checks if the user already exists. If not, it sends a
    verification code to the provided phone number for registration purposes.

    - **Parameters**:
        - `data`: The registration data including `phone_number`.

    - **Responses**:
        - **200**: Verification code sent successfully.
        - **400**: If a user with the provided phone number already exists.

    - **Example**:
        ```json
        {
            "success": true,
            "message": "Verification code sent to +998 xx xxx xx xx"
        }
        ```
    """
    if await User.user_exists(data.phone_number, db):
        raise HTTPException(status_code=400, detail=_("User with this phone number already exists."))

    await AuthService.send_verification_code(data.phone_number, "register")
    return {"success": True,
            "message": _("Verification code sent to {phone_number}").format(phone_number=data.phone_number)}


# Register a new user
@router.post("/register", status_code=status.HTTP_200_OK)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_session)):
    """
    Register a new user after verifying the OTP.

    This endpoint verifies the provided OTP for the specified phone number.
    If the OTP is valid, it creates a new user and returns the access and refresh tokens.

    - **Parameters**:
        - `data`: The registration data including `phone_number`, `password`, and `verification_code`.

    - **Responses**:
        - **200**: User registered successfully with tokens.
        - **400**: Invalid OTP or OTP expired.

    - **Example**:
        ```json
        {
            "success": true,
            "access": "jwt_access_token",
            "refresh": "jwt_refresh_token",
            "token_type": "bearer",
            "message": "Registration successful!"
        }
        ```
    """
    otp = await OTPManager.get_otp(data.phone_number, "register")

    if not otp or otp != data.verification_code:
        raise HTTPException(status_code=400, detail=_("Invalid OTP or OTP expired."))
    async with db.begin():
        try:
            user = await User.create_user(data.phone_number, data.password, db)
            await OTPManager.delete_otp(data.phone_number, "register")

            access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": user.phone_number}, expires_delta=access_token_expires)
            refresh_token = create_refresh_token(data={"sub": user.phone_number})

            return {
                "success": True,
                "access": access_token,
                "refresh": refresh_token,
                "token_type": "bearer",
                "message": _("Registration successful!")
            }
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=_("An error occurred during registration: ") + str(e))
