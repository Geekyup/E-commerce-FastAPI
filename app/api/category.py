from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.category import (
    create_category, get_category, list_categories, update_category, delete_category
)

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await create_category(db, payload)


@router.get("", response_model=list[CategoryOut])
async def get_list(db: AsyncSession = Depends(get_db)):
    return await list_categories(db)


@router.get("/{category_id}", response_model=CategoryOut)
async def get_one(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=CategoryOut)
async def update(category_id: int, payload: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    category = await get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await update_category(db, category, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await delete_category(db, category)