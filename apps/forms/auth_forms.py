import re

from pydantic import BaseModel, constr, field_validator

from utils.translations import trans as _


def validate_phone_format(phone_number: str) -> str:
    """Validate and normalize the phone number format for Uzbek numbers."""

    cleaned_number = re.sub(r'\D', '', phone_number)

    if cleaned_number.startswith('998'):
        cleaned_number = cleaned_number[3:]

    if len(cleaned_number) == 9:
        return f'+998{cleaned_number}'

    if len(cleaned_number) == 2:
        return f'+998{cleaned_number}'

    raise ValueError(_("Invalid phone number format. Use formats like +998 xx xxx xx xx"))


def validate_password(password: str) -> str:
    """Validate the password according to specified rules."""
    if len(password) < 8:
        raise ValueError(_("Password must be at least 8 characters long."))

    if not re.search(r'[A-Z]', password):
        raise ValueError(_("Password must contain at least one uppercase letter."))

    if not re.search(r'[a-z]', password):
        raise ValueError(_("Password must contain at least one lowercase letter."))

    if not re.search(r'[0-9]', password):
        raise ValueError(_("Password must contain at least one digit."))

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError(_("Password must contain at least one special character."))

    return password


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

    @field_validator('password')
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v)


class PreLoginRequest(BaseRequest):
    """Request model for pre-login."""
    password: constr(min_length=8)


class LoginRequest(BaseRequest):
    """Request model for login."""
    password: constr(min_length=8, max_length=60)
    verification_code: constr(min_length=5, max_length=5)


class PreResetPassword(BaseRequest):
    """Request model for pre-resetting the password."""
    pass


class ResetPassword(BaseRequest):
    """Request model for resetting the password."""
    password: constr(min_length=8, max_length=60)
    verification_code: constr(min_length=5, max_length=5)

    @field_validator('password')
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v)
