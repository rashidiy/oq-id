from fastapi import HTTPException, status, Request
from starlette.responses import JSONResponse

from forms.auth import PreRegisterRequest, RegisterRequest
from managers import PassManager
from models.users import User
from utils.services import AuthService, TokenManager
from utils.translations import trans as _
from .base import router


@router.post("/pre_register", status_code=status.HTTP_200_OK)
async def pre_register(request: Request, data: PreRegisterRequest):
    """
    Pre-register a new user by sending a verification code.

    Parameters:
    - data: An instance of PreRegisterRequest containing the user's phone number.

    Returns:
      - A dictionary with two keys: "success" and "message".

    Raises:
    - HTTPException: If a user with the provided phone number already exists.
    """
    user = await User.get_by(phone_number=data.phone_number)
    if user:
        raise HTTPException(status_code=400, detail=_("User with this phone number already exists."))

    await AuthService.send_verification_code(request, data.phone_number, "register")
    return JSONResponse(content={
        "success": True,
        "message": _(f"Verification code sent to {data.phone_number}")
    })


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
    await AuthService.verify_otp(data.phone_number, data.verification_code, "register")

    user = await User.get_by(phone_number=data.phone_number)
    if user:
        raise HTTPException(status_code=400, detail=_("User with this phone number already exists."))

    user = await User.create(phone_number=data.phone_number,
                             password_hash=PassManager.hash_password(data.password))

    access_token = TokenManager.create_access_token(data={"sub": user.phone_number})
    refresh_token = TokenManager.create_refresh_token(data={"sub": user.phone_number})

    return JSONResponse(content={
        "success": True,
        "access": access_token,
        "refresh": refresh_token,
        "token_type": "bearer",
        "message": _("Registration successful!")
    })
