from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    role: str
    active: bool
    created_at: datetime
    last_login: datetime | None = None


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    display_name: str = ""
    role: Literal["admin", "user"] = "user"
    active: bool = True


class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=6, max_length=128)
    display_name: str | None = None
    role: Literal["admin", "user"] | None = None
    active: bool | None = None
