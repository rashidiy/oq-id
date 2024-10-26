from fastapi import HTTPException, status

from forms.auth import PreRegisterRequest, RegisterRequest
from managers import PassManager
from models.users import User
from utils.services import OTPManager, AuthService, TokenManager
from utils.translations import trans as _
from .base import router


@router.post("/pre_register", status_code=status.HTTP_200_OK)
async def pre_register(data: PreRegisterRequest):
    """
    Pre-register a new user by sending a verification code.

    Parameters:
    - data: An instance of PreRegisterRequest containing the user's phone number.

    Returns:
      - A dictionary with two keys: "success" and "message".

    Raises:
    - HTTPException: If a user with the provided phone number already exists.
    """
    if await User.get_by(phone_number=data.phone_number):
        raise HTTPException(status_code=400, detail=_("User with this phone number already exists."))

    await AuthService.send_verification_code(data.phone_number, "register")
    return {"success": True,
            "message": _("Verification code sent to {phone_number}").format(phone_number=data.phone_number)}


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(data: RegisterRequest):
    """
    Registers a new user by verifying the OTP and creating an access and refresh token.

    Parameters:
    - data : An instance of RegisterRequest containing the user's phone number and password.

    Returns:
        - A dictionary datas:

    Raises:
    - HTTPException: If the provided OTP is invalid or expired.
    - HTTPException: If a user with the provided phone number already exists.
    """
    otp = await OTPManager.get_otp(data.phone_number, "register")
    if not otp or otp != data.verification_code:
        raise HTTPException(status_code=400, detail=_("Invalid OTP or OTP expired."))

    if await User.get_by(phone_number=data.phone_number):
        raise HTTPException(status_code=400, detail=_("User with this phone number already exists."))

    user = await User.create(phone_number=data.phone_number,
                             password_hash=PassManager.hash_password(data.password))

    await OTPManager.delete_otp(data.phone_number, "register")
    access_token = TokenManager.create_access_token(data={"sub": user.phone_number})
    refresh_token = TokenManager.create_refresh_token(data={"sub": user.phone_number})

    return {
        "success": True,
        "access": access_token,
        "refresh": refresh_token,
        "token_type": "bearer",
        "message": _("Registration successful!")
    }
