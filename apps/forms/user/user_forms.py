from typing import Optional

from pydantic import BaseModel, Field


class UserUpdateRequest(BaseModel):
    """Request model for updating users details."""
    first_name: Optional[str] = Field(default=None, title="First Name")
    last_name: Optional[str] = Field(default=None, title="Last Name")
    gender: Optional[str] = Field(default=None, title="Gender")
    birth_date: Optional[str] = Field(default=None, title="Birth Date (YYYY-MM-DD)")
    bio: Optional[str] = Field(default=None, title="Bio")
    avatar: Optional[str] = Field(default=None, title="Avatar URL")
    developer_mode: Optional[bool] = Field(default=None, title="Developer Mode")
