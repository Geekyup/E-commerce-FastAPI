from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:12345@127.0.0.1:5432/fastapi_test"

    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGIN_REGEX: str = (
        r"^(https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?|null)$"
    )
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:3000",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]
    )

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600
    JWT_REFRESH_TOKEN_EXPIRES: int = 604800

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()