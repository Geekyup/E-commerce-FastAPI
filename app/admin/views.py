from fastadmin import SqlAlchemyModelAdmin, register
from sqlalchemy import select, delete
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.core.security import verify_password
from app.db.session import AsyncSessionLocal


@register(User, sqlalchemy_sessionmaker=AsyncSessionLocal)
class UserAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "username", "email", "is_active", "is_superuser", "created_at")
    list_display_links = ("id", "username")
    search_fields = ("username", "email")
    ordering = ("id",)
    exclude = ("hashed_password", "cart")

    async def authenticate(self, username: str, password: str):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalars().first()
            if not user or not user.is_superuser:
                return None
            if not verify_password(password, user.hashed_password):
                return None
            return user.id

    async def orm_get_obj(self, id):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            return await session.get(User, int(id))

    async def orm_save_obj(self, id, payload: dict):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            if id:
                obj = await session.get(User, int(id))
                if not obj:
                    return None
                for k, v in payload.items():
                    setattr(obj, k, v)
                await session.merge(obj)
                await session.commit()
            else:
                obj = User(**payload)
                session.add(obj)
                await session.commit()
            return await session.get(User, getattr(obj, self.get_model_pk_name(User)))

    async def orm_delete_obj(self, id):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            obj = await session.get(User, int(id))
            if obj is None:
                raise ValueError("User not found.")
            await session.delete(obj)
            await session.commit()


@register(Product, sqlalchemy_sessionmaker=AsyncSessionLocal)
class ProductAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "title", "price", "inventory")
    list_display_links = ("id", "title")
    search_fields = ("title", "description")
    ordering = ("id",)

    async def orm_get_obj(self, id):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            return await session.get(Product, int(id))

    async def orm_save_obj(self, id, payload: dict):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            if id:
                obj = await session.get(Product, int(id))
                if not obj:
                    return None
                for k, v in payload.items():
                    setattr(obj, k, v)
                await session.merge(obj)
                await session.commit()
            else:
                obj = Product(**payload)
                session.add(obj)
                await session.commit()
            return await session.get(Product, getattr(obj, self.get_model_pk_name(Product)))

    async def orm_delete_obj(self, id):
        async with AsyncSessionLocal() as session:
            from app.models.cart import CartItem
            await session.execute(
                delete(CartItem).where(CartItem.product_id == int(id))
            )
            await session.execute(
                delete(Product).where(Product.id == int(id))
            )
            await session.commit()


@register(Category, sqlalchemy_sessionmaker=AsyncSessionLocal)
class CategoryAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "name", "description")
    list_display_links = ("id", "name")
    search_fields = ("name", "description")
    ordering = ("id",)

    async def orm_get_obj(self, id):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            return await session.get(Category, int(id))

    async def orm_save_obj(self, id, payload: dict):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            if id:
                obj = await session.get(Category, int(id))
                if not obj:
                    return None
                for k, v in payload.items():
                    setattr(obj, k, v)
                await session.merge(obj)
                await session.commit()
            else:
                obj = Category(**payload)
                session.add(obj)
                await session.commit()
            return await session.get(Category, getattr(obj, self.get_model_pk_name(Category)))

    async def orm_delete_obj(self, id):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            obj = await session.get(Category, int(id))
            if obj is None:
                raise ValueError("Category not found.")
            await session.delete(obj)
            await session.commit()