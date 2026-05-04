from pydantic import BaseModel, ConfigDict, Field

# Добавить товар в корзину
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)  # минимум 1

# Обновить количество
class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)

# Ответ — одна позиция
class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)
# Ответ — вся корзина
class CartOut(BaseModel):
    id: int
    items: list[CartItemOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)