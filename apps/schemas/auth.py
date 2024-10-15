from pydantic import BaseModel


class User(BaseModel):
    id: int
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str
