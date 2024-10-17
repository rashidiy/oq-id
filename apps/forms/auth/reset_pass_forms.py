from pydantic import constr, field_validator

from forms.auth import BaseRequest
from utils.validators import validate_password


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
