from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from authx import TokenPayload

from app.db.session import get_db
from app.core.security import auth
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderOut,
    OrderListOut,
    OrderItemCreate,
    OrderItemOut,
    OrderStatus,
)
from app.services.order import (
    create_order,
    get_order,
    get_user_orders,
    list_all_orders,
    update_order,
    delete_order,
    add_item_to_order,
    update_order_item,
    remove_order_item,
    count_user_orders,
)

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    user_id: int,
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await create_order(user_id=user_id, payload=payload, db=db)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderOut)
async def get_order_endpoint(
    order_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(order_id=order_id, db=db)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")
    return order


@router.get("", response_model=list[OrderListOut])
async def list_user_orders_endpoint(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: OrderStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_orders(
        user_id=user_id,
        db=db,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.patch("/{order_id}", response_model=OrderOut)
async def update_order_endpoint(
    order_id: int,
    user_id: int,
    payload: OrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(order_id=order_id, db=db)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")

    try:
        order = await update_order(order=order, payload=payload, db=db)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_endpoint(
    order_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(order_id=order_id, db=db)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")

    await delete_order(order=order, db=db)


@router.post("/{order_id}/items", response_model=OrderItemOut, status_code=status.HTTP_201_CREATED)
async def add_item_endpoint(
    order_id: int,
    user_id: int,
    payload: OrderItemCreate,
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(order_id=order_id, db=db)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")

    try:
        item = await add_item_to_order(order=order, payload=payload, db=db)
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{order_id}/items/{item_id}", response_model=OrderItemOut)
async def update_item_endpoint(
    order_id: int,
    item_id: int,
    user_id: int,
    quantity: int = Query(..., gt=0),
    unit_price: float | None = Query(default=None, gt=0),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(order_id=order_id, db=db)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")

    try:
        item = await update_order_item(
            item_id=item_id,
            quantity=quantity,
            unit_price=unit_price,
            order=order,
            db=db,
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_endpoint(
    order_id: int,
    item_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    order = await get_order(order_id=order_id, db=db)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")

    try:
        await remove_order_item(item_id=item_id, order=order, db=db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/stats")
async def get_user_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    count = await count_user_orders(user_id=user_id, db=db)
    return {"user_id": user_id, "total_orders": count}
