from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(username: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(payload: UserCreate, db: AsyncSession) -> User:
    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(user: User, payload: UserUpdate, db: AsyncSession) -> User:
    if payload.email is not None:
        user.email = payload.email
    if payload.username is not None:
        user.username = payload.username
    if payload.password is not None:
        user.hashed_password = get_password_hash(payload.password)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(user: User, db: AsyncSession) -> None:
    await db.delete(user)
    await db.commit()


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User | None:
    user = await get_user_by_email(email, db)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user