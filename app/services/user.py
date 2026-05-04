from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(payload: UserCreate, db: AsyncSession) -> User:
    # Проверяем что email и username свободны
    existing_email = await get_user_by_email(payload.email, db)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email уже занят")

    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username уже занят")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession) -> User:
    user = await get_user_by_id(user_id, db)

    if payload.email:
        existing = await get_user_by_email(payload.email, db)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email уже занят")
        user.email = payload.email

    if payload.username:
        result = await db.execute(select(User).where(User.username == payload.username))
        existing = result.scalar_one_or_none()
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Username уже занят")
        user.username = payload.username

    if payload.password:
        user.hashed_password = hash_password(payload.password)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(user_id: int, db: AsyncSession) -> None:
    user = await get_user_by_id(user_id, db)
    await db.delete(user)
    await db.commit()


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    return user