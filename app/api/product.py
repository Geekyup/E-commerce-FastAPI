from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.product import (
    ProductInActiveCartsError,
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    product = await create_product(db, payload)
    return product


@router.get("/{product_id}", response_model=ProductOut)
async def get_product_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    product = await get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("", response_model=list[ProductOut])
async def list_products_endpoint(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category_id: int | None = Query(default=None),  
    db: AsyncSession = Depends(get_db),
):
    return await list_products(db, limit=limit, offset=offset, category_id=category_id)


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product_api(
    product_id: int,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await get_product(db, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")

    obj = await update_product(db, obj, payload)
    return obj


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    product = await get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        await delete_product(db, product)
    except ProductInActiveCartsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product is present in one or more carts",
        )
    return None