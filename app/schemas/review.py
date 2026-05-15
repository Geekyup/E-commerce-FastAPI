from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    rating: float = Field(..., ge=1, le=5)
    title: str = Field(..., max_length=200)
    comment: Optional[str] = Field(default=None)


class ReviewCreate(ReviewBase):
    product_id: int
    user_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(default=None, ge=1, le=5)
    title: Optional[str] = Field(default=None, max_length=200)
    comment: Optional[str] = Field(default=None)


class ReviewOut(ReviewBase):
    id: int
    product_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewWithUserOut(ReviewBase):
    id: int
    product_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class User(BaseModel):
        id: int
        username: str
        model_config = ConfigDict(from_attributes=True)
    
    user: User
    
    model_config = ConfigDict(from_attributes=True)
