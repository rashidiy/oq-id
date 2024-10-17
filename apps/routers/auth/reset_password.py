from fastapi import HTTPException, status

from forms.auth.reset_pass_forms import (PreResetPassword, ResetPassword)
from models.users import User
from utils.services import OTPManager, AuthService
from utils.translations import trans as _
from .base import router


# Pre-reset password
@router.post("/pre_reset_password")
async def pre_reset_password(data: PreResetPassword):
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
    user = await User.get_user_by_phone_number(data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("User with this phone number does not exist."))

    await AuthService.send_verification_code(data.phone_number, "reset_password")
    return {"success": True, "message": _("Verification code has been sent successfully.")}


# Reset password
@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetPassword):
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
    otp = await OTPManager.get_otp(data.phone_number, "reset_password")

    if not otp or otp != data.verification_code:
        raise HTTPException(status_code=400, detail=_("Invalid OTP or OTP expired."))

    user = await User.get_user_by_phone_number(data.phone_number)
    if not user:
        raise HTTPException(status_code=400, detail=_("User does not exist."))

    user.password_hash = User.hash_password(data.password)
    await User.update_user(user)

    await OTPManager.delete_otp(data.phone_number, "reset_password")

    return {"success": True, "message": _("Password reset successful!")}
