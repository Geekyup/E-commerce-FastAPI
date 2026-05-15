from __future__ import annotations

from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart: Mapped[Cart | None] = relationship("Cart", back_populates="user", uselist=False)
    orders: Mapped[list[Order]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews: Mapped[list[Review]] = relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"