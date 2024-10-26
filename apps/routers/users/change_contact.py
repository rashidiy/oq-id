from fastapi import Depends, HTTPException
from starlette import status

from forms.user import ChangePhoneEmailRequest, VerifyRequest
from models.users import User
from utils.services import AuthService, OTPManager, TokenManager
from utils.translations import trans as _
from utils.validators import validate_phone_format
from .base import router


@router.post("/change_contact", status_code=status.HTTP_200_OK)
async def change_contact(data: ChangePhoneEmailRequest, user: User = Depends(User.current)):
    """
    This function handles the contact change request for a user. It checks if a new phone number or email is provided,
    validates the format, checks for existing users, sends verification codes, and updates the user's contact information.

    Parameters:
    - data (json): containing the new phone number and email.
    - user (User, optional): The current user making the request. Defaults to the user returned by User.current.

    Returns:
    - A dictionary containing success status, message, and optionally, the access and refresh tokens if the phone number is changed.
    - Raises HTTPException with appropriate status code and detail if any validation or error occurs.
    """
    try:
        if data.phone_number and data.phone_number != "Null":
            validated_phone_number = validate_phone_format(data.phone_number)
            existing_user = await User.get_by(phone_number=validated_phone_number)

            if existing_user:
                raise HTTPException(status_code=400, detail=_("This phone number is already in use."))

            if validated_phone_number == user.phone_number:
                raise HTTPException(status_code=400, detail=_("You cannot change to your current phone number."))

            await AuthService.send_verification_code(validated_phone_number, "change_phone")

            return {
                "success": True,
                "message": _("Verification code sent to {phone}.").format(phone=validated_phone_number)
            }

        if data.email and data.email != "Null":
            if data.email != user.email:
                existing_email_user = await User.get_by(email=data.email)
                if existing_email_user:
                    raise HTTPException(status_code=400, detail=_("This email is already in use."))

                await AuthService.send_verification_code(data.email, "change_email")
                return {
                    "success": True,
                    "message": _("Verification code sent to {email}.").format(email=data.email)
                }
        raise HTTPException(status_code=400, detail=_("No new contact information provided."))

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.patch("/verify_contact_change")
async def verify_contact_change(data: VerifyRequest, user: User = Depends(User.current)):
    """
    This function verifies the contact change request for a user. It checks if a new phone number or email is provided,
    validates the format, checks for existing users, verifies the verification code, and updates the user's contact information.

    Parameters:
    - data (json): A data object containing the new phone number, email, and verification code.
    - user (User, optional): The current user making the request. Defaults to the user returned by User.current.

    Returns:
    - A dictionary containing success status, message, and optionally, the access and refresh tokens if the phone number is changed.
    - Raises HTTPException with appropriate status code and detail if any validation or error occurs.
    """
    if data.new_phone and data.new_phone != 'Null':
        validated_phone_number = validate_phone_format(data.new_phone)

        if not validated_phone_number:
            raise HTTPException(status_code=400, detail=_("Invalid phone number format!"))

        otp = await OTPManager.get_otp(validated_phone_number, "change_phone")
        if not otp or otp != data.vc_code:
            raise HTTPException(status_code=400, detail=_("Invalid verification code or expired!"))
        user.phone_number = validated_phone_number
        await User.update(user)

        access_token = TokenManager.create_access_token(data={"sub": validated_phone_number})
        refresh_token = TokenManager.create_refresh_token(data={"sub": validated_phone_number})

        return {
            "success": True,
            "message": _("Phone number has been changed to {new_phone}.".format(new_phone=validated_phone_number)),
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    if data.new_email and data.new_email != 'Null':
        otp = await OTPManager.get_otp(data.new_email, "change_email")
        if not otp or otp != data.vc_code:
            raise HTTPException(status_code=400, detail=_("Invalid verification code or expired."))

        user.email = data.new_email
        await User.update(user)

        return {
            "success": True,
            "message": _(f"Email has been changed to {data.new_email}.")
        }

    raise HTTPException(status_code=400, detail=_("No new contact information provided."))
