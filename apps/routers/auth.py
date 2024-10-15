from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from forms.auth_forms import (LoginRequest, PreLoginRequest, PreRegisterRequest,
                              PreResetPassword, RegisterRequest, ResetPassword)
from models.users import User
from settings.config import Config, get_session
from utils.helpers import (delete_vc_from_redis, get_user_by_phone_number,
                           get_vc_from_redis, is_rate_limit_exceeded,
                           send_verification_code, user_exists)
from utils.jwt import create_access_token, create_refresh_token, verify_token
from utils.password import hash_password, verify_password
from utils.translations import _  # noqa

router = APIRouter()
http_bearer = HTTPBearer()


# Pre-register a user
@router.post("/pre_register", status_code=status.HTTP_200_OK)
async def pre_register(
        data: PreRegisterRequest,
        db: AsyncSession = Depends(get_session)
):
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
            "message": "Verification code sent to +1234567890"
        }
        ```
    """
    if await user_exists(data.phone_number, db):
        raise HTTPException(status_code=400, detail=_("User with this phone number already exists."))

    await send_verification_code(data.phone_number, "register")
    return {"success": True,
            "message": _("Verification code sent to {phone_number}").format(phone_number=data.phone_number)}


# Register a new user
@router.post("/register", status_code=status.HTTP_200_OK)
async def register(
        data: RegisterRequest,
        db: AsyncSession = Depends(get_session)
):
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
    otp = await get_vc_from_redis(data.phone_number, "register")

    if not otp or otp != data.verification_code:
        raise HTTPException(status_code=400, detail=_("Invalid OTP or OTP expired."))

    user = User(
        phone_number=data.phone_number,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await delete_vc_from_redis(data.phone_number, "register")

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


# Pre-login a user
@router.post("/pre_login", status_code=status.HTTP_200_OK)
async def pre_login(
        data: PreLoginRequest,
        db: AsyncSession = Depends(get_session)
):
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
    user = await get_user_by_phone_number(db, data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("User with this phone number does not exist."))

    if not verify_password(data.password, str(user.password_hash)):
        raise HTTPException(status_code=400, detail=_("Invalid password."))

    if await is_rate_limit_exceeded(data.phone_number, "login"):
        raise HTTPException(status_code=429, detail=_("Too many OTP requests for login. Please try again later."))

    await send_verification_code(data.phone_number, "login")
    return {"success": True, "message": _("Verification code has been sent successfully.")}


# Login a user
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
        data: LoginRequest,
        db: AsyncSession = Depends(get_session)
):
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
    user = await get_user_by_phone_number(db, data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("Invalid phone number or user does not exist."))

    if not verify_password(data.password, str(user.password_hash)):
        raise HTTPException(status_code=400, detail=_("Invalid password."))

    otp = await get_vc_from_redis(data.phone_number, "login")
    if not otp or otp != data.verification_code:
        raise HTTPException(status_code=400, detail=_("Invalid validation code or it has expired."))

    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.phone_number}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.phone_number})

    await delete_vc_from_redis(data.phone_number, "login")

    return {
        "success": True,
        "access": access_token,
        "refresh": refresh_token,
        "token_type": "bearer",
        "message": _("Login successful!")
    }


# Pre-reset password
@router.post("/pre_reset_password")
async def pre_reset_password(
        data: PreResetPassword,
        db: AsyncSession = Depends(get_session)
):
    """
    Pre-reset the password by sending a verification code.

    This endpoint checks if the user exists and sends an OTP to the
    provided phone number for password reset.

    - **Parameters**:
        - `data`: The request data including `phone_number`.

    - **Responses**:
        - **200**: Verification code sent successfully.
        - **400**: User does not exist.

    - **Example**:
        ```json
        {
            "success": true,
            "message": "Verification code has been sent successfully."
        }
        ```
    """
    user = await get_user_by_phone_number(db, data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("User with this phone number does not exist."))

    await send_verification_code(data.phone_number, "reset_password")
    return {"success": True, "message": _("Verification code has been sent successfully.")}


# Reset password
@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(
        data: ResetPassword,
        db: AsyncSession = Depends(get_session)
):
    """
    Reset the user's password after verifying the OTP.

    This endpoint validates the OTP and updates the user's password if valid.

    - **Parameters**:
        - `data`: The reset data including `phone_number`, `verification_code`, and `password`.

    - **Responses**:
        - **200**: Password reset successfully.
        - **400**: Invalid OTP or user does not exist.

    - **Example**:
        ```json
        {
            "success": true,
            "message": "Password reset successful!"
        }
        ```
    """
    otp = await get_vc_from_redis(data.phone_number, "reset_password")

    if not otp or otp != data.verification_code:
        raise HTTPException(status_code=400, detail=_("Invalid OTP or OTP expired."))

    user = await get_user_by_phone_number(db, data.phone_number)
    if user:
        user.password_hash = hash_password(data.password)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        await delete_vc_from_redis(data.phone_number, "reset_password")

        return {"success": True, "message": _("Password reset successful!")}

    raise HTTPException(status_code=400, detail=_("User does not exist."))


# Get current user information
@router.get("/get_me")
async def protected_route(
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
        db: AsyncSession = Depends(get_session)
):
    """
    Get the current authenticated user's information.

    This endpoint retrieves user details if the provided token is valid.

    - **Parameters**:
        - `credentials`: Authorization credentials containing the bearer token.

    - **Responses**:
        - **200**: User information retrieved successfully.
        - **404**: User not found.

    - **Example**:
        ```json
        {
            "message": "You are authorized!",
            "user": {
                "user_id": 1,
                "phone_number": "+1234567890"
            }
        }
        ```
    """
    token = credentials.credentials
    payload = verify_token(token)

    user = await get_user_by_phone_number(db, payload['sub'])

    if user is None:
        raise HTTPException(status_code=404, detail=_("User not found"))

    return {
        "message": _("You are authorized!"),
        "user": {
            "user_id": user.id,
            "phone_number": user.phone_number,
        }
    }
