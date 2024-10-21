from pydantic import BaseModel, constr


class AppRequest(BaseModel):
    app_id: int


class TokenRegenerateConfirm(AppRequest):
    verification_code: constr(min_length=5, max_length=5)
