from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class ProductBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Decimal = Field(..., gt=0)

class ProductCreate(ProductBase):
    inventory: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Optional[Decimal] = Field(default=None, gt=0)
    inventory: Optional[int] = Field(default=None, ge=0)

class ProductOut(ProductBase):
    id: int
    inventory: int

    model_config = ConfigDict(from_attributes=True)