import re

from pydantic import BaseModel, constr, field_validator
from utils.translations import _

def validate_phone_format(phone_number: str) -> str:
    """Validate the phone number format using regex."""
    pattern = r'^(\+998|998|)?\s?(\d{2})\s?(\d{3})\s?(\d{2})\s?(\d{2})$'
    if not re.match(pattern, phone_number):
        raise ValueError(_("Invalid phone number format. Use formats like +998 xx xxx xx xx."))
    return phone_number


class BaseRequest(BaseModel):
    """Base model to handle common phone number validation."""
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        return validate_phone_format(v)


class PreRegisterRequest(BaseRequest):
    """Request model for pre-registration."""
    pass


class RegisterRequest(BaseRequest):
    """Request model for registration."""
    password: constr(min_length=8, max_length=100)
    verification_code: constr(min_length=5, max_length=5)


class PreLoginRequest(BaseRequest):
    """Request model for pre-login."""
    password: constr(min_length=8)


class LoginRequest(BaseRequest):
    """Request model for login."""
    password: constr(min_length=8)
    verification_code: constr(min_length=5, max_length=5)


class PreResetPassword(BaseRequest):
    """Request model for pre-resetting the password."""
    pass


class ResetPassword(BaseRequest):
    """Request model for resetting the password."""
    password: constr(min_length=8)
    verification_code: constr(min_length=5, max_length=5)
