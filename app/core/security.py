import bcrypt
from authx import AuthX, AuthXConfig

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


auth = AuthX(
    config=AuthXConfig(
        JWT_SECRET_KEY=settings.JWT_SECRET_KEY,
        JWT_ALGORITHM=settings.JWT_ALGORITHM,
        JWT_TOKEN_LOCATION=["headers"],
        JWT_ACCESS_TOKEN_EXPIRES=settings.JWT_ACCESS_TOKEN_EXPIRES,
        JWT_REFRESH_TOKEN_EXPIRES=settings.JWT_REFRESH_TOKEN_EXPIRES,
        JWT_HEADER_NAME="Authorization",
        JWT_HEADER_TYPE="Bearer",
    )
)