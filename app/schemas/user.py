from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(default=None)
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
    password: Optional[str] = Field(default=None, min_length=6)


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"