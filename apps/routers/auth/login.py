from fastapi import HTTPException, status, Request
from forms.auth import PreLoginRequest, LoginRequest
from managers import PassManager
from models.users import User
from utils.services import AuthService, TokenManager
from utils.translations import trans as _
from .base import router


@router.post("/pre_login", status_code=status.HTTP_200_OK)
async def pre_login(data: PreLoginRequest, request: Request):
    """
    Pre-login endpoint for a user. Sends a verification code to the user's phone number.

    Parameters:
    - data (PreLoginRequest): Contains the user's phone number and password.

    Returns:
    - dict: Success status and a message indicating the verification code has been sent.
    """
    user = await User.get_by(phone_number=data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("User with this phone number does not exist."))

    if not PassManager.verify_password(data.password, str(user.password_hash)):
        raise HTTPException(status_code=400, detail=_("Invalid password."))

    await AuthService.send_verification_code(request, data.phone_number, "login")
    return {
        "success": True,
        "message": _(f"Verification code sent to {data.phone_number}"),
    }


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data: LoginRequest):
    """
    Authenticates a user by verifying their phone number, password, and OTP.

    Parameters:
    - data : Contains the user's phone number, password, and verification code.

    Returns:
    - dict: Success status, tokens, and a message.
    """
    user = await User.get_by(phone_number=data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("Invalid phone number or user does not exist."))

    if not PassManager.verify_password(data.password, str(user.password_hash)):
        raise HTTPException(status_code=400, detail=_("Invalid password."))

    await AuthService.verify_otp(data.phone_number, data.verification_code, "login")

    access_token = TokenManager.create_access_token(data={"sub": user.phone_number})
    refresh_token = TokenManager.create_refresh_token(data={"sub": user.phone_number})

    return {
        "success": True,
        "access": access_token,
        "refresh": refresh_token,
        "token_type": "bearer",
    }
