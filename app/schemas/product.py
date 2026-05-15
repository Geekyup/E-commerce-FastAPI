from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

from app.schemas.category import CategoryOut


class ProductBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Decimal = Field(..., gt=0)
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    inventory: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Optional[Decimal] = Field(default=None, gt=0)
    inventory: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None


class ReviewInProduct(BaseModel):
    id: int
    rating: float
    title: str
    comment: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class ProductOut(ProductBase):
    id: int
    inventory: int
    cover_image: Optional[str] = None
    images: Optional[list[str]] = None
    category: Optional[CategoryOut] = None
    reviews: Optional[list[ReviewInProduct]] = None

    model_config = ConfigDict(from_attributes=True)