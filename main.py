from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastadmin import fastapi_app as admin_app
import uvicorn
import app.db.base
from dotenv import load_dotenv
load_dotenv() 

import app.admin.views  # важно: импортируем для регистрации через @register

from app.api.cart import router as cart_router
from app.api.product import router as product_router
from app.api.user import router as user_router
from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal  # нужен async session


app = FastAPI(title="FastAPI Test")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(user_router)
app.include_router(cart_router)

# Монтируем fastadmin
app.mount("/admin", admin_app)


@app.get("/")
async def root():
    return {"message": "Server is running"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )