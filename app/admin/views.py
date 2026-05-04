from fastadmin import SqlAlchemyModelAdmin, register
from app.models.product import Product
from app.models.user import User
from app.core.security import verify_password
from app.db.session import AsyncSessionLocal


@register(User)
class UserAdmin(SqlAlchemyModelAdmin):
    db_session_maker = AsyncSessionLocal

    list_display = ("id", "username", "email", "is_active", "is_superuser", "created_at")
    list_display_links = ("id", "username")
    search_fields = ("username", "email")
    ordering = ("id",)
    exclude = ("hashed_password", "cart")

    async def authenticate(self, username: str, password: str):
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalars().first()

            if not user:
                return None
            if not user.is_superuser:
                return None
            if not verify_password(password, user.hashed_password):
                return None

            return user.id

    async def orm_get_obj(self, id): 
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.id == int(id))
            )
            return result.scalars().first()

    async def orm_delete_obj(self, id):
        async with AsyncSessionLocal() as session:
            from sqlalchemy import delete
            await session.execute(
                delete(User).where(User.id == int(id))
            )
            await session.commit()


@register(Product)
class ProductAdmin(SqlAlchemyModelAdmin):
    db_session_maker = AsyncSessionLocal

    list_display = ("id", "title", "price", "inventory")
    list_display_links = ("id", "title")
    search_fields = ("title", "description")
    ordering = ("id",)

    async def orm_get_obj(self, id):
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Product).where(Product.id == int(id))
            )
            return result.scalars().first()

    async def orm_delete_obj(self, id):
        async with AsyncSessionLocal() as session:
            from sqlalchemy import delete
            from app.models.cart import CartItem  

            await session.execute(
                delete(CartItem).where(CartItem.product_id == int(id))
            )
            
            await session.execute(
                delete(Product).where(Product.id == int(id))
            )
            await session.commit()