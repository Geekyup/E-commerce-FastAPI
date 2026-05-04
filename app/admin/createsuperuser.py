import asyncio
import app.db.base  
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def main():
    username = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")

    async with SessionLocal() as session:
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        print(f"Суперпользователь '{username}' создан")

asyncio.run(main())