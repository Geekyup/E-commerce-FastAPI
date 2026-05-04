from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.cart import Cart, CartItem
from app.schemas.cart import CartItemAdd, CartItemUpdate


async def get_or_create_cart(user_id: int, db: AsyncSession) -> Cart:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items))
    )
    cart = result.scalar_one_or_none()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        cart.items = []

    return cart


async def add_item_to_cart(user_id: int, payload: CartItemAdd, db: AsyncSession) -> Cart:
    cart = await get_or_create_cart(user_id, db)

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == payload.product_id,
        )
    )
    item = result.scalar_one_or_none()

    if item:
        item.quantity += payload.quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        db.add(item)

    await db.commit()
    return await get_or_create_cart(user_id, db)


async def update_cart_item(
    item_id: int, payload: CartItemUpdate, db: AsyncSession
) -> CartItem:
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Позиция не найдена")

    item.quantity = payload.quantity
    await db.commit()
    await db.refresh(item)
    return item


async def remove_cart_item(item_id: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Позиция не найдена")

    await db.delete(item)
    await db.commit()


async def clear_cart(user_id: int, db: AsyncSession) -> None:
    cart = await get_or_create_cart(user_id, db)

    for item in cart.items:
        await db.delete(item)

    await db.commit()