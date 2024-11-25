from fastapi import Depends, HTTPException, Request
from starlette import status

from forms.user import ChangePhoneEmailRequest, VerifyRequest
from models.users import User
from utils.services import AuthService, TokenManager
from utils.translations import trans as _
from utils.validators import validate_phone_format
from .base import router


@router.patch("/change_contact", status_code=status.HTTP_200_OK)
async def change_contact(request: Request, data: ChangePhoneEmailRequest, user: User = Depends(User.current)):
    """
    Handles the contact change request for a user, ensuring only one of phone or email is provided,
    validates the format, checks for existing users, sends verification codes, and updates the user's contact information.
    """
    if data.phone_number:
        validated_phone_number = validate_phone_format(data.phone_number)

        if validated_phone_number == user.phone_number:
            raise HTTPException(status_code=400, detail=_("You cannot change to your current phone number."))

        existing_user = await User.get_by(phone_number=validated_phone_number)
        if existing_user:
            raise HTTPException(status_code=400, detail=_("This phone number is already in use."))

        await AuthService.send_verification_code(request, validated_phone_number, "change_phone")
        return {
            "success": True,
            "message": _(f"Verification code sent to {data.phone_number}.")
        }

    if data.email:
        if data.email == user.email:
            raise HTTPException(status_code=400, detail=_("You cannot change to your current email address."))

        existing_email_user = await User.get_by(email=data.email)
        if existing_email_user:
            raise HTTPException(status_code=400, detail=_("This email is already in use."))

        await AuthService.send_verification_code(request, data.email, "change_email")
        return {
            "success": True,
            "message": _(f"Verification code sent to {data.email}.")
        }

    raise HTTPException(status_code=400, detail=_("No new contact information provided."))


@router.patch("/verify_contact_change")
async def verify_contact_change(data: VerifyRequest, user: User = Depends(User.current)):
    """
    Verifies the contact change request for a user by checking the OTP and updating contact information.
    """
    if data.new_phone:
        validated_phone_number = validate_phone_format(data.new_phone)

        if not validated_phone_number:
            raise HTTPException(status_code=400, detail=_("Invalid phone number format!"))

        await AuthService.verify_otp(validated_phone_number, data.vc_code, "change_phone")
        user.phone_number = validated_phone_number
        await User.update(user)

        access_token = TokenManager.create_access_token(data={"sub": validated_phone_number})
        refresh_token = TokenManager.create_refresh_token(data={"sub": validated_phone_number})

        return {
            "success": True,
            "message": _(f"Phone number has been changed to {data.new_phone}."),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "type": "bearer"
        }

    if data.new_email:
        await AuthService.verify_otp(data.new_email, data.vc_code, "change_email")
        user.email = data.new_email
        await User.update(user)

        return {
            "success": True,
            "message": _(f"Email has been changed to {data.new_email}.")
        }
    raise HTTPException(status_code=400, detail=_("No new contact information provided."))
