from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional
import json

from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.upload import delete_upload_file, parse_images_json, images_to_json


class ProductInActiveCartsError(Exception):
    pass


async def create_product(db: AsyncSession, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product, attribute_names=['category'])
    return product


async def get_product(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.category), selectinload(Product.reviews))
    )
    return result.scalar_one_or_none()


async def list_products(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    category_id: Optional[int] = None, 
) -> list[Product]:
    query = select(Product).options(selectinload(Product.category), selectinload(Product.reviews)).order_by(Product.id)
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    result = await db.execute(query.limit(limit).offset(offset))
    return list(result.scalars().all())


async def update_product(
    db: AsyncSession, product: Product, payload: ProductUpdate
) -> Product:
    for field, value in payload.model_dump(exclude_unset=True).items():
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
    
    # Удаляем файлы при удалении товара
    if product.cover_image:
        delete_upload_file(product.cover_image)
    if product.images:
        images = parse_images_json(product.images)
        for image_path in images:
            delete_upload_file(image_path)
    
    try:
        await db.delete(product)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ProductInActiveCartsError from exc