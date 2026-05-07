from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from authx import TokenPayload

from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserOut, TokenOut
from app.services.user import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    update_user,
    delete_user,
    authenticate_user,
)
from app.core.security import auth

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(payload.email, db):
        raise HTTPException(status_code=400, detail="Email уже занят")
    if await get_user_by_username(payload.username, db):
        raise HTTPException(status_code=400, detail="Username уже занят")
    return await create_user(payload, db)


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(payload.email, payload.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")
    return TokenOut(
        access_token=auth.create_access_token(uid=str(user.id)),
        refresh_token=auth.create_refresh_token(uid=str(user.id)),
    )


@router.post("/refresh", response_model=TokenOut)
async def refresh(payload: TokenPayload = Depends(auth.refresh_token_required)):
    return TokenOut(
        access_token=auth.create_access_token(uid=payload.sub),
        refresh_token=auth.create_refresh_token(uid=payload.sub),
    )


@router.get("/me", response_model=UserOut)
async def get_me(
    payload: TokenPayload = Depends(auth.access_token_required),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(int(payload.sub), db)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(
    payload_data: UserUpdate,
    payload: TokenPayload = Depends(auth.access_token_required),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(int(payload.sub), db)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if payload_data.email:
        existing = await get_user_by_email(payload_data.email, db)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Email уже занят")
    if payload_data.username:
        existing = await get_user_by_username(payload_data.username, db)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Username уже занят")
    return await update_user(user, payload_data, db)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    payload: TokenPayload = Depends(auth.access_token_required),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(int(payload.sub), db)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await delete_user(user, db)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    _: TokenPayload = Depends(auth.access_token_required),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user