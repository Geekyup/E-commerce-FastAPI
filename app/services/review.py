from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional

from app.models.review import Review
from app.models.product import Product
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate


async def create_review(db: AsyncSession, payload: ReviewCreate) -> Review:
    # Проверяем существование товара и пользователя
    product_result = await db.execute(select(Product).where(Product.id == payload.product_id))
    if product_result.scalar_one_or_none() is None:
        raise ValueError("Product not found")
    
    user_result = await db.execute(select(User).where(User.id == payload.user_id))
    if user_result.scalar_one_or_none() is None:
        raise ValueError("User not found")
    
    review = Review(**payload.model_dump())
    db.add(review)
    await db.commit()
    await db.refresh(review, attribute_names=['product', 'user'])
    
    # Пересчитываем средний рейтинг товара
    await recalculate_average_rating(db, payload.product_id)
    
    return review


async def get_review(db: AsyncSession, review_id: int) -> Review | None:
    result = await db.execute(
        select(Review)
        .where(Review.id == review_id)
        .options(selectinload(Review.user), selectinload(Review.product))
    )
    return result.scalar_one_or_none()


async def get_product_reviews(
    db: AsyncSession,
    product_id: int,
    limit: int = 10,
    offset: int = 0,
) -> list[Review]:
    result = await db.execute(
        select(Review)
        .where(Review.product_id == product_id)
        .options(selectinload(Review.user))
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_user_reviews(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
    offset: int = 0,
) -> list[Review]:
    result = await db.execute(
        select(Review)
        .where(Review.user_id == user_id)
        .options(selectinload(Review.product))
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def update_review(
    db: AsyncSession, review: Review, payload: ReviewUpdate
) -> Review:
    product_id = review.product_id
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, field, value)
    await db.commit()
    await db.refresh(review, attribute_names=['product', 'user'])
    
    # Пересчитываем средний рейтинг товара
    await recalculate_average_rating(db, product_id)
    
    return review


async def delete_review(db: AsyncSession, review: Review) -> None:
    if review is None:
        return
    product_id = review.product_id
    await db.delete(review)
    await db.commit()
    
    # Пересчитываем средний рейтинг товара
    await recalculate_average_rating(db, product_id)


async def recalculate_average_rating(db: AsyncSession, product_id: int) -> float | None:
    """Пересчитываем среднее значение рейтинга для товара"""
    result = await db.execute(
        select(func.avg(Review.rating))
        .where(Review.product_id == product_id)
    )
    avg_rating = result.scalar()
    
    # Получаем товар и обновляем его рейтинг
    product_result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = product_result.scalar_one_or_none()
    
    if product:
        product.average_rating = float(avg_rating) if avg_rating else None
        await db.commit()
        await db.refresh(product)
    
    return product.average_rating if product else None