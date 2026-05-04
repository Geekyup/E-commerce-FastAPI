from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductInActiveCartsError(Exception):
    pass


async def create_product(db: AsyncSession, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def get_product(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def list_products(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
) -> list[Product]:
    result = await db.execute(
        select(Product).order_by(Product.id).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def update_product(
    db: AsyncSession,
    product: Product,
    payload: ProductUpdate,
) -> Product:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product: Product) -> None:
    if product is None:
        return

    result = await db.execute(
        select(CartItem.id).where(CartItem.product_id == product.id).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        raise ProductInActiveCartsError

    try:
        await db.delete(product)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ProductInActiveCartsError from exc