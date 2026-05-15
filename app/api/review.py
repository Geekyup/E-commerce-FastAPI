from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.review import ReviewCreate, ReviewOut, ReviewUpdate, ReviewWithUserOut
from app.services.review import (
    create_review,
    delete_review,
    get_review,
    get_product_reviews,
    get_user_reviews,
    update_review,
)

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review_endpoint(
    payload: ReviewCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создать новый отзыв о товаре"""
    try:
        review = await create_review(db, payload)
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review_endpoint(
    review_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить отзыв по ID"""
    review = await get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/product/{product_id}", response_model=list[ReviewWithUserOut])
async def get_product_reviews_endpoint(
    product_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Получить все отзывы о товаре"""
    return await get_product_reviews(db, product_id, limit=limit, offset=offset)


@router.get("/user/{user_id}", response_model=list[ReviewWithUserOut])
async def get_user_reviews_endpoint(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Получить все отзывы пользователя"""
    return await get_user_reviews(db, user_id, limit=limit, offset=offset)


@router.patch("/{review_id}", response_model=ReviewOut)
async def update_review_endpoint(
    review_id: int,
    payload: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновить отзыв"""
    review = await get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review = await update_review(db, review, payload)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review_endpoint(
    review_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удалить отзыв"""
    review = await get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    
    await delete_review(db, review)
    return None
