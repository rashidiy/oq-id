from pydantic import BaseModel, field_validator

from utils.validators import validate_phone_format


class BaseRequest(BaseModel):
    """Base model to handle common phone number validation."""
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        return validate_phone_format(v)


from .reset_pass_forms import PreResetPassword, ResetPassword
from .login_forms import PreLoginRequest, LoginRequest
from .register_forms import PreRegisterRequest, RegisterRequest
