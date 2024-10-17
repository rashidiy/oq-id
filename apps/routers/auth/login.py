from datetime import timedelta

from fastapi import HTTPException, status

from forms.auth_forms import (LoginRequest, PreLoginRequest)
from models.users import User
from settings.config import Config
from utils.helpers import (OTPManager, AuthService)
from utils.jwt import create_access_token, create_refresh_token
from utils.password import verify_password
from utils.translations import trans as _
from .base import router


@router.post("/pre_login", status_code=status.HTTP_200_OK)
async def pre_login(data: PreLoginRequest):
    """
    Pre-login a user by sending a verification code to their phone number.

    This endpoint verifies if the user exists and sends an OTP to the
    provided phone number for login purposes.

    - **Parameters**:
        - `data`: The login request data including `phone_number` and `password`.

    - **Responses**:
        - **200**: OTP sent successfully.
        - **400**: User does not exist or invalid password.
        - **429**: Too many OTP requests.

    - **Example**:
        ```json
        {
            "success": true,
            "message": "Verification code has been sent successfully."
        }
        ```
    """
    user = await User.get_user_by_phone_number(data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("User with this phone number does not exist."))

    if not verify_password(data.password, str(user.password_hash)):
        raise HTTPException(status_code=400, detail=_("Invalid password."))

    await AuthService.send_verification_code(data.phone_number, "login")
    return {"success": True,
            "message": _("Verification code sent to {phone_number}").format(phone_number=data.phone_number)}


# Login a user
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data: LoginRequest):
    """
    Log in a user after verifying the OTP.

    This endpoint validates the provided OTP and logs the user in,
    returning access and refresh tokens.

    - **Parameters**:
        - `data`: The login data including `phone_number`, `password`, and `verification_code`.

    - **Responses**:
        - **200**: User logged in successfully with tokens.
        - **400**: Invalid phone number, user does not exist, or invalid verification code.

    - **Example**:
        ```json
        {
            "success": true,
            "access": "jwt_access_token",
            "refresh": "jwt_refresh_token",
            "token_type": "bearer",
            "message": "Login successful!"
        }
        ```
    """
    user = await User.get_user_by_phone_number(data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("Invalid phone number or user does not exist."))

    if not verify_password(data.password, str(user.password_hash)):
        raise HTTPException(status_code=400, detail=_("Invalid password."))

    otp = await OTPManager.get_otp(data.phone_number, "login")
    if not otp or otp != data.verification_code:
        raise HTTPException(status_code=400, detail=_("Invalid validation code or it has expired."))

    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.phone_number}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.phone_number})

    await OTPManager.delete_otp(data.phone_number, "login")

    return {
        "success": True,
        "access": access_token,
        "refresh": refresh_token,
        "token_type": "bearer",
        "message": _("Login successful!")
    }
