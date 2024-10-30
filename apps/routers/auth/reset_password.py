from fastapi import HTTPException, status, Request

from forms.auth.reset_pass_forms import PreResetPassword, ResetPassword
from managers import PassManager
from models import User
from utils.services import AuthService, TokenManager
from utils.translations import trans as _
from .base import router


@router.post("/pre_reset_password")
async def pre_reset_password(request: Request, data: PreResetPassword):
    """
    Send a verification code to the user's phone number for password reset.

    Parameters:
    - data (PreResetPassword): User's phone number.

    Returns:
    - dict: A dictionary with 'success' and 'message' keys.
    """
    user = await User.get_by(phone_number=data.phone_number)
    if not user:
        raise HTTPException(status_code=400,
                            detail=_(f"User with this phone number {data.phone_number} does not exist."))

    await AuthService.send_verification_code(request, data.phone_number, "reset_password")

    return {"success": True, "message": _("Verification code has been sent successfully.")}


@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetPassword):
    """
    Reset the user's password using a verification code sent to their phone number.

    Parameters:
    - data (ResetPassword): User's phone number, verification code, and new password.

    Returns:
    - dict: A dictionary with 'success' and 'message' keys.
    """
    await AuthService.verify_otp(data.phone_number, data.verification_code, "reset_password")

    user = await User.get_by(phone_number=data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("User does not exist."))

    user.password_hash = PassManager.hash_password(data.password)
    await User.update(user)

    return {"success": True, "message": _("Password reset successful!")}


@router.post("/refresh_token", response_model=dict)
async def refresh_access_token(refresh_token: str):
    """
    Refresh the access token using the refresh token.

    Parameters:
    - refresh_token (str): The refresh token.

    Returns:
    - dict: A dictionary containing the new access token.
    """
    payload = TokenManager.verify_token(refresh_token)
    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail=_("Invalid token type. Only refresh tokens are allowed."))

    new_access_token = TokenManager.create_access_token(data={"sub": payload["sub"]})
    return {"access_token": new_access_token}
