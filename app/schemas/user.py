from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


# Регистрация
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6)


# Обновление профиля
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=100)
    password: str | None = Field(default=None, min_length=6)


# Ответ — без пароля
class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Логин
class UserLogin(BaseModel):
    email: EmailStr
    password: str