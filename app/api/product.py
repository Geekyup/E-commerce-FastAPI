from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import json

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
from app.services.upload import save_upload_file, delete_upload_file, parse_images_json, images_to_json

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


@router.post("/{product_id}/cover", response_model=ProductOut)
async def upload_cover_image(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить обложку для товара"""
    product = await get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Удаляем старую обложку если она есть
        if product.cover_image:
            delete_upload_file(product.cover_image)
        
        # Сохраняем новую обложку
        file_path = await save_upload_file(file, subfolder="products/covers")
        product.cover_image = file_path
        
        await db.commit()
        await db.refresh(product)
        return product
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")


@router.post("/{product_id}/images", response_model=ProductOut)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить фото товара"""
    product = await get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Сохраняем новое фото
        file_path = await save_upload_file(file, subfolder="products/images")
        
        # Добавляем к существующим фото
        images = parse_images_json(product.images) if product.images else []
        images.append(file_path)
        product.images = images_to_json(images)
        
        await db.commit()
        await db.refresh(product)
        return product
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")


@router.delete("/{product_id}/images/{image_index}")
async def delete_product_image(
    product_id: int,
    image_index: int,
    db: AsyncSession = Depends(get_db),
):
    """Удалить фото товара по индексу"""
    product = await get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    images = parse_images_json(product.images) if product.images else []
    
    if image_index < 0 or image_index >= len(images):
        raise HTTPException(status_code=400, detail="Invalid image index")
    
    # Удаляем файл
    deleted_image = images.pop(image_index)
    delete_upload_file(deleted_image)
    
    # Обновляем список
    product.images = images_to_json(images) if images else None
    
    await db.commit()
    await db.refresh(product)
    return product