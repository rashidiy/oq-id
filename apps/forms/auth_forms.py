import re

from pydantic import BaseModel, constr, field_validator


def validate_phone_format(phone_number: str) -> str:
    """Validate the phone number format using regex."""
    pattern = r'^(\+998|998|)?\s?(\d{2})\s?(\d{3})\s?(\d{2})\s?(\d{2})$'
    if not re.match(pattern, phone_number):
        raise ValueError("Invalid phone number format. Use formats like +998 90 123 45 67.")
    return phone_number


class PreRegisterRequest(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        return validate_phone_format(v)


class RegisterRequest(BaseModel):
    phone_number: str
    password: constr(min_length=8, max_length=100)
    verification_code: constr(min_length=5, max_length=5)

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        return validate_phone_format(v)


class PreLoginRequest(BaseModel):
    phone_number: str
    password: constr(min_length=8)

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        return validate_phone_format(v)


class LoginRequest(BaseModel):
    phone_number: str
    password: constr(min_length=8)
    verification_code: constr(min_length=5, max_length=5)

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        return validate_phone_format(v)


class PreResetPassword(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        return validate_phone_format(v)


class ResetPassword(BaseModel):
    phone_number: str
    password: constr(min_length=8)
    verification_code: constr(min_length=5, max_length=5)

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        return validate_phone_format(v)
