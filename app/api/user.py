from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserOut
from app.services.user import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    authenticate_user,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(payload, db)


@router.post("/login", response_model=UserOut)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(payload.email, payload.password, db)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_by_id(user_id, db)


@router.patch("/{user_id}", response_model=UserOut)
async def update(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)):
    return await update_user(user_id, payload, db)


@router.delete("/{user_id}", status_code=204)
async def delete(user_id: int, db: AsyncSession = Depends(get_db)):
    await delete_user(user_id, db)