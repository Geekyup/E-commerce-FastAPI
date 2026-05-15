from __future__ import annotations

from sqlalchemy import String, Numeric, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db.base_class import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    inventory: Mapped[int] = mapped_column(Integer, default=0)
    cover_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    images: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    average_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)

    category: Mapped[Optional[Category]] = relationship('Category', back_populates="products")
    reviews: Mapped[list[Review]] = relationship('Review', back_populates="product", cascade="all, delete-orphan")