from pydantic import constr

from forms.auth import BaseRequest


class PreLoginRequest(BaseRequest):
    """Request model for pre-login."""
    password: constr(min_length=8)


class LoginRequest(BaseRequest):
    """Request model for login."""
    password: constr(min_length=8, max_length=60)
    verification_code: constr(min_length=5, max_length=5)
