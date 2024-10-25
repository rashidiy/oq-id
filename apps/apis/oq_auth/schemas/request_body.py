from fastapi import HTTPException
from pydantic import BaseModel, constr, field_validator
from starlette import status

from utils.translations import trans as _


class TokenValidator(BaseModel):
    token: constr(min_length=59, max_length=60)

    @field_validator('token')
    def validate_token(cls, value):
        if ':' not in value:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_('Invalid token'))
        if not value.split(':')[0].isdigit():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_('Invalid token'))
        return value


class PermissionSchema(TokenValidator):
    user_id: int
