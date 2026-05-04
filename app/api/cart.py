from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartOut, CartItemOut
from app.services.cart import (
    get_or_create_cart,
    add_item_to_cart,
    update_cart_item,
    remove_cart_item,
    clear_cart,
)

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartOut)
async def get_cart(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_or_create_cart(user_id, db)


@router.post("/add", response_model=CartOut)
async def add_item(user_id: int, payload: CartItemAdd, db: AsyncSession = Depends(get_db)):
    return await add_item_to_cart(user_id, payload, db)


@router.patch("/item/{item_id}", response_model=CartItemOut)
async def update_item(
    item_id: int, payload: CartItemUpdate, db: AsyncSession = Depends(get_db)
):
    return await update_cart_item(item_id, payload, db)


@router.delete("/item/{item_id}")
async def remove_item(item_id: int, db: AsyncSession = Depends(get_db)):
    await remove_cart_item(item_id, db)
    return {"status": "удалено"}


@router.delete("/clear")
async def clear(user_id: int, db: AsyncSession = Depends(get_db)):
    await clear_cart(user_id, db)
    return {"status": "корзина очищена"}