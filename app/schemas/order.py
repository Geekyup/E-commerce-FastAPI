from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    name: str = Field(..., max_length=255)
    sku: Optional[str] = Field(default=None, max_length=100)


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, gt=0)
    unit_price: Optional[Decimal] = Field(default=None, gt=0)


class OrderItemOut(OrderItemBase):
    id: int
    order_id: int
    name: str
    sku: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    status: Optional[OrderStatus] = OrderStatus.PENDING
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    payment_method: Optional[str] = Field(default=None, max_length=50)
    shipping_cost: Decimal = Field(default=Decimal("0.00"), ge=0)


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    payment_method: Optional[str] = Field(default=None, max_length=50)
    shipping_cost: Optional[Decimal] = Field(default=None, ge=0)
    items: Optional[List[OrderItemCreate]] = None


class OrderOut(OrderBase):
    id: int
    user_id: int
    total_amount: Decimal
    items: List[OrderItemOut]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderListOut(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
