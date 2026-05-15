from fastadmin import SqlAlchemyModelAdmin, register
from sqlalchemy import select, delete
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.review import Review
from app.models.cart import Cart, CartItem
from app.core.security import verify_password
from app.db.session import AsyncSessionLocal


@register(User, sqlalchemy_sessionmaker=AsyncSessionLocal)
class UserAdmin(SqlAlchemyModelAdmin):
    name = "User"
    name_plural = "Users"
    list_display = ("id", "username", "email", "is_active", "is_superuser", "created_at", "updated_at")
    list_display_links = ("id", "username")
    search_fields = ("username", "email")
    ordering = ("-created_at",)
    fields = ("username", "email", "is_active", "is_superuser")
    exclude = ("hashed_password", "cart", "orders", "reviews", "created_at", "updated_at")
    page_size = 50
    icon = "fa-solid fa-user"

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
    name = "Product"
    name_plural = "Products"
    list_display = ("id", "title", "price", "inventory", "category_id", "average_rating", "cover_image")
    list_display_links = ("id", "title")
    search_fields = ("title", "description")
    ordering = ("-id",)
    fields = ("title", "description", "price", "inventory", "category_id", "cover_image", "images", "average_rating")
    page_size = 50
    icon = "fa-solid fa-box"


@register(Category, sqlalchemy_sessionmaker=AsyncSessionLocal)
class CategoryAdmin(SqlAlchemyModelAdmin):
    name = "Category"
    name_plural = "Categories"
    list_display = ("id", "name", "description")
    list_display_links = ("id", "name")
    search_fields = ("name", "description")
    ordering = ("id",)
    page_size = 50
    icon = "fa-solid fa-tag"


@register(Order, sqlalchemy_sessionmaker=AsyncSessionLocal)
class OrderAdmin(SqlAlchemyModelAdmin):
    name = "Order"
    name_plural = "Orders"
    list_display = ("id", "user_id", "status", "total_amount", "created_at")
    list_display_links = ("id",)
    search_fields = ("id", "user_id", "status")
    ordering = ("-created_at",)
    exclude = ("items",)
    page_size = 50
    icon = "fa-solid fa-receipt"


@register(OrderItem, sqlalchemy_sessionmaker=AsyncSessionLocal)
class OrderItemAdmin(SqlAlchemyModelAdmin):
    name = "Order Item"
    name_plural = "Order Items"
    list_display = ("id", "order_id", "product_id", "name", "quantity", "unit_price")
    list_display_links = ("id",)
    search_fields = ("name", "sku")
    ordering = ("order_id",)
    page_size = 50
    icon = "fa-solid fa-list"


@register(Review, sqlalchemy_sessionmaker=AsyncSessionLocal)
class ReviewAdmin(SqlAlchemyModelAdmin):
    name = "Review"
    name_plural = "Reviews"
    list_display = ("id", "product_id", "user_id", "rating", "title", "created_at")
    list_display_links = ("id", "title")
    search_fields = ("title", "comment")
    ordering = ("-created_at",)
    exclude = ("created_at", "updated_at")
    page_size = 50
    icon = "fa-solid fa-star"


@register(Cart, sqlalchemy_sessionmaker=AsyncSessionLocal)
class CartAdmin(SqlAlchemyModelAdmin):
    name = "Cart"
    name_plural = "Carts"
    list_display = ("id", "user_id")
    list_display_links = ("id",)
    search_fields = ("user_id",)
    ordering = ("id",)
    exclude = ("items",)
    page_size = 50
    icon = "fa-solid fa-shopping-cart"


@register(CartItem, sqlalchemy_sessionmaker=AsyncSessionLocal)
class CartItemAdmin(SqlAlchemyModelAdmin):
    name = "Cart Item"
    name_plural = "Cart Items"
    list_display = ("id", "cart_id", "product_id", "quantity")
    list_display_links = ("id",)
    search_fields = ("product_id",)
    ordering = ("cart_id",)
    page_size = 50
    icon = "fa-solid fa-cart-shopping"