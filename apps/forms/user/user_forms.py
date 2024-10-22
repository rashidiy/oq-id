from typing import Optional

from pydantic import BaseModel, Field
from pydantic.v1 import root_validator


class UserUpdateRequest(BaseModel):
    """Request model for updating users details."""
    first_name: Optional[str] = Field(default=None, title="First Name")
    last_name: Optional[str] = Field(default=None, title="Last Name")
    gender: Optional[str] = Field(default=None, title="Gender")
    birth_date: Optional[str] = Field(default=None, title="Birth Date (YYYY-MM-DD)")
    bio: Optional[str] = Field(default=None, title="Bio")
    avatar: Optional[str] = Field(default=None, title="Avatar URL")
    developer_mode: Optional[bool] = Field(default=None, title="Developer Mode")


class ChangePhoneEmailRequest(BaseModel):
    """Request model for changing phone number or email."""
    phone_number: Optional[str] = Field(default='Null', title='Phone Number')
    email: Optional[str] = Field(default='Null', title='Email Address')


class VerifyRequest(BaseModel):
    """Request model for verifying the OTP sent to the user's phone or email."""
    vc_code: str = Field(default='', title="Verification Code")
    new_phone: Optional[str] = Field(default='Null', title="New Phone Number")
    new_email: Optional[str] = Field(default='Null', title="New Email Address")

    @root_validator
    def validate_new_contact(cls, values):
        phone = values.get('new_phone')
        email = values.get('new_email')
        if not phone and not email:
            raise ValueError("Either new phone number or email must be provided.")
        if phone and email:
            raise ValueError("Provide either a new phone number or email, not both.")
        return values
