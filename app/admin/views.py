from fastadmin import SqlAlchemyModelAdmin, register
from sqlalchemy import select, delete
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.review import Review
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
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalars().first()
            if not user or not user.is_superuser:
                return None
            if not verify_password(password, user.hashed_password):
                return None
            return user.id


@register(Product, sqlalchemy_sessionmaker=AsyncSessionLocal)
class ProductAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "title", "price", "inventory", "cover_image")
    list_display_links = ("id", "title")
    search_fields = ("title", "description")
    ordering = ("id",)
    fields = ("title", "description", "price", "inventory", "category_id", "cover_image", "images")


@register(Category, sqlalchemy_sessionmaker=AsyncSessionLocal)
class CategoryAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "name", "description")
    list_display_links = ("id", "name")
    search_fields = ("name", "description")
    ordering = ("id",)


@register(Order, sqlalchemy_sessionmaker=AsyncSessionLocal)
class OrderAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "user_id", "status", "total_amount", "created_at")
    list_display_links = ("id",)
    search_fields = ("id", "user_id", "status")
    ordering = ("-created_at",)
    exclude = ("items",)


@register(OrderItem, sqlalchemy_sessionmaker=AsyncSessionLocal)
class OrderItemAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "order_id", "product_id", "name", "quantity", "unit_price")
    list_display_links = ("id",)
    search_fields = ("name", "sku")
    ordering = ("order_id",)


@register(Review, sqlalchemy_sessionmaker=AsyncSessionLocal)
class ReviewAdmin(SqlAlchemyModelAdmin):
    name = "Review"
    name_plural = "Reviews"
    list_display = ("id", "product_id", "user_id", "rating", "title", "created_at")
    list_display_links = ("id", "title")
    search_fields = ("title", "comment")
    ordering = ("-created_at",)
    # Отключаем создание и редактирование через админ-панель
    # Используй API endpoint /api/reviews для создания отзывов
    exclude = ("created_at", "updated_at")