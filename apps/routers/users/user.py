from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from starlette import status

from forms.user import ChangePhoneEmailRequest, VerifyRequest, UserUpdateRequest
from models.users import User
from utils.services import AuthService, OTPManager, TokenManager
from utils.translations import trans as _
from utils.validators import validate_phone_format

router = APIRouter(prefix="/api/v1", tags=["Users"])
http_bearer = HTTPBearer()


@router.get("/get_me")
async def get_me(user: User = Depends(User.current)):
    """
    Retrieve the current user's information.

    This endpoint returns the details of the currently authenticated user.

    - **Responses**:
        - **200**: User details retrieved successfully.
        - **404**: If the user is not found.

    - **Example**:
        ```json
        {
            "success": true,
            "datas": {
                "id": 1,
                "phone_number": "+998 xx xxx xx xx",
                "email": "user@example.com",
                "birth_date": "1990-01-01"
            }
        }
        ```
    """

    if not user:
        raise HTTPException(status_code=404, detail=_("User not found"))

    return {
        "success": True,
        "datas": user.to_dict
    }


@router.patch("/update_user", response_model=dict)
async def patch_user(update_data: UserUpdateRequest, user: User = Depends(User.current)):
    """
    Update the current user's information.

    This function allows updating various fields of the current user's profile.
    It validates and updates the user's datas and other fields as provided.

    Parameters:
    - update_data (UserUpdateRequest): The data containing fields to be updated.
    - user (User): The current user object, automatically provided by dependency injection.

    Returns:
    - dict: A dictionary indicating the success of the operation and the updated user data.
    """
    for field, value in update_data:
        if value is not None:
            if field == "birth_date":
                try:
                    user.birth_date = datetime.strptime(value, '%d.%m.%Y').date()
                except ValueError:
                    raise HTTPException(status_code=400, detail=_("Invalid date format. Use DD.MM.YYYY."))
            else:
                setattr(user, field, value)

    await User.update_user(user)
    return {"success": True, "message": _("User updated successfully"), "datas": user.to_dict}


@router.post("/change_contact", status_code=status.HTTP_200_OK)
async def change_contact(data: ChangePhoneEmailRequest, user: User = Depends(User.current)):
    """
    Initiate the process to change the user's contact information.

    This endpoint sends a verification code to the new phone number or email
    provided by the user for contact change.

    - **Parameters**:
        - `data`: The new contact information including `phone_number` and/or `email`.

    - **Responses**:
        - **200**: Verification code sent successfully.
        - **400**: If the new phone number or email is already in use, or if no new information is provided.

    - **Example**:
        ```json
        {
            "success": true,
            "message": "Verification code sent to +998 xx xxx xx xx. Or user@example.com"
        }
        ```
    """
    try:
        if data.phone_number and data.phone_number != "Null":
            validated_phone_number = validate_phone_format(data.phone_number)
            existing_user = await User.get_user_by_phone_number(validated_phone_number)

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
                existing_email_user = await User.get_user_by_email(data.email)
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
    Verify the new contact information change.

    This endpoint checks the provided verification code and updates the user's
    contact information if the code is valid.

    - **Parameters**:
        - `data`: Contains the new contact information and the verification code.

    - **Responses**:
        - **200**: Contact information updated successfully.
        - **400**: Invalid verification code or no new contact information provided.

    - **Example**:
        ```json
        {
            "success": true,
            "message": "Phone number has been changed to +998 xx xxx xx xx.",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR..."
        }
        ```
    """
    if data.new_phone and data.new_phone != 'Null':
        validated_phone_number = validate_phone_format(data.new_phone)

        if not validated_phone_number:
            raise HTTPException(status_code=400, detail=_("Invalid phone number format."))

        otp = await OTPManager.get_otp(validated_phone_number, "change_phone")
        if not otp or otp != data.vc_code:
            raise HTTPException(status_code=400, detail=_("Invalid verification code or expired."))
        user.phone_number = validated_phone_number
        await User.update_user(user)

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
        await User.update_user(user)

        return {
            "success": True,
            "message": _("Email has been changed to {email}.".format(email=data.new_email))
        }

    raise HTTPException(status_code=400, detail=_("No new contact information provided."))
