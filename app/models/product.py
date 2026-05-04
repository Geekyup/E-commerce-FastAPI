from sqlalchemy import String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    inventory: Mapped[int] = mapped_column(Integer, default=0)