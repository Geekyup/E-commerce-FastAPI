from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastadmin import fastapi_app as admin_app
from dotenv import load_dotenv
import uvicorn
import app.db.base
import app.admin.views

from app.core.config import settings
from app.core.security import auth          
from app.db.session import engine, AsyncSessionLocal

from app.api.cart import router as cart_router
from app.api.product import router as product_router
from app.api.user import router as user_router
from app.api.category import router as category_router


load_dotenv()

app = FastAPI(title="FastAPI Test")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth.handle_errors(app)     
               
app.include_router(product_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(category_router)

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