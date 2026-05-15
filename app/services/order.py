from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from decimal import Decimal

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate, OrderItemCreate


# ============ Order CRUD ============

async def create_order(user_id: int, payload: OrderCreate, db: AsyncSession) -> Order:
    """
    Создать новый заказ с товарами.
    Загружает все продукты одним запросом, проверяет их наличие,
    затем создаёт заказ и позиции.
    """
    product_ids = [item.product_id for item in payload.items]

    products_result = await db.execute(
        select(Product).where(Product.id.in_(product_ids))
    )
    
    products_map: dict[int, Product] = {}

    # 2. Получаем список всех найденных товаров из базы
    all_products = products_result.scalars().all()

    # 3. Начинаем перебирать их по одному
    for p in all_products:
        # 4. Кладем в словарь: ID товара будет ключом, а сам товар — значением
        products_map[p.id] = p
    # Проверяем, что все запрошенные товары существуют

    for pid in product_ids:
        if pid not in products_map:
            raise ValueError(f"Товар с ID {pid} не найден")

    order = Order(
        user_id=user_id,
        status=payload.status or OrderStatus.PENDING,
        shipping_cost=payload.shipping_cost,
        shipping_address=payload.shipping_address,
        billing_address=payload.billing_address,
        payment_method=payload.payment_method,
    )

    for item in payload.items:
        if item.quantity <= 0:
            raise ValueError(f"Количество товара с ID {item.product_id} должно быть больше 0")

        order_item = OrderItem(
            product_id=item.product_id,
            name=item.name,
            sku=item.sku,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        order.items.append(order_item)

    calculate_order_total(order)

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def get_order(order_id: int, db: AsyncSession) -> Order | None:
    """Получить заказ по ID вместе с позициями и пользователем."""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items), selectinload(Order.user))
    )
    return result.scalar_one_or_none()


async def get_user_orders(
    user_id: int,
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    status: Optional[OrderStatus] = None,
) -> list[Order]:
    """Получить заказы конкретного пользователя с фильтрацией по статусу."""
    return await _fetch_orders(
        db=db,
        limit=limit,
        offset=offset,
        status=status,
        user_id=user_id,
    )


async def list_all_orders(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    status: Optional[OrderStatus] = None,
) -> list[Order]:
    """Получить все заказы (для администраторов)."""
    return await _fetch_orders(db=db, limit=limit, offset=offset, status=status)


async def _fetch_orders(
    db: AsyncSession,
    limit: int,
    offset: int,
    status: Optional[OrderStatus] = None,
    user_id: Optional[int] = None,
) -> list[Order]:
    """Внутренняя функция для получения заказов с общей логикой фильтрации."""
    query = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.user))
        .order_by(Order.created_at.desc())
    )

    if user_id is not None:
        query = query.where(Order.user_id == user_id)

    if status is not None:
        query = query.where(Order.status == status)

    result = await db.execute(query.limit(limit).offset(offset))
    return list(result.scalars().all())


async def update_order(
    order: Order,
    payload: OrderUpdate,
    db: AsyncSession,
) -> Order:
    """
    Обновить заказ. При передаче новых позиций — пересчитывает сумму.
    """
    if payload.status is not None:
        order.status = payload.status
    if payload.shipping_address is not None:
        order.shipping_address = payload.shipping_address
    if payload.billing_address is not None:
        order.billing_address = payload.billing_address
    if payload.payment_method is not None:
        order.payment_method = payload.payment_method
    if payload.shipping_cost is not None:
        order.shipping_cost = payload.shipping_cost

    if payload.items is not None:
        product_ids = [item.product_id for item in payload.items]
        products_result = await db.execute(
            select(Product).where(Product.id.in_(product_ids))
        )
        products_map: dict[int, Product] = {
            p.id: p for p in products_result.scalars().all()
        }

        for pid in product_ids:
            if pid not in products_map:
                raise ValueError(f"Товар с ID {pid} не найден")

        order.items.clear()

        for item in payload.items:
            if item.quantity <= 0:
                raise ValueError(
                    f"Количество товара с ID {item.product_id} должно быть больше 0"
                )
            order_item = OrderItem(
                product_id=item.product_id,
                name=item.name,
                sku=item.sku,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            order.items.append(order_item)

    calculate_order_total(order)

    await db.commit()
    await db.refresh(order)
    return order


async def delete_order(order: Order, db: AsyncSession) -> None:
    """Удалить заказ. Если заказ не передан — ничего не делаем."""
    if order is None:
        return
    await db.delete(order)
    await db.commit()


# ============ Order Item CRUD ============

async def add_item_to_order(
    order: Order,
    payload: OrderItemCreate,
    db: AsyncSession,
) -> OrderItem:
    """Добавить позицию в существующий заказ и пересчитать итог."""
    if payload.quantity <= 0:
        raise ValueError("Количество должно быть больше 0")

    product_result = await db.execute(
        select(Product).where(Product.id == payload.product_id)
    )
    product_obj = product_result.scalar_one_or_none()
    if not product_obj:
        raise ValueError(f"Товар с ID {payload.product_id} не найден")

    order_item = OrderItem(
        order_id=order.id,
        product_id=payload.product_id,
        name=payload.name,
        sku=payload.sku,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
    )

    order.items.append(order_item)
    calculate_order_total(order)

    db.add(order_item)
    await db.commit()
    await db.refresh(order_item)
    return order_item


async def update_order_item(
    item_id: int,
    quantity: int,
    unit_price: Optional[Decimal],
    order: Order,
    db: AsyncSession,
) -> OrderItem:
    """
    Обновить количество и/или цену позиции в заказе.
    Количество должно быть >= 1.
    """
    if quantity <= 0:
        raise ValueError("Количество должно быть больше 0")

    result = await db.execute(
        select(OrderItem).where(OrderItem.id == item_id)
    )
    order_item = result.scalar_one_or_none()

    if not order_item or order_item.order_id != order.id:
        raise ValueError("Позиция заказа не найдена")

    order_item.quantity = quantity

    if unit_price is not None:
        if unit_price <= 0:
            raise ValueError("Цена должна быть больше 0")
        order_item.unit_price = unit_price

    calculate_order_total(order)

    await db.commit()
    await db.refresh(order_item)
    return order_item


async def remove_order_item(
    item_id: int,
    order: Order,
    db: AsyncSession,
) -> None:
    """
    Удалить позицию из заказа и пересчитать итог.
    Сначала убираем из коллекции — потом пересчитываем, потом удаляем из БД.
    """
    result = await db.execute(
        select(OrderItem).where(OrderItem.id == item_id)
    )
    order_item = result.scalar_one_or_none()

    if not order_item or order_item.order_id != order.id:
        raise ValueError("Позиция заказа не найдена")

    # Сначала убираем из in-memory коллекции, потом пересчитываем
    order.items = [item for item in order.items if item.id != item_id]
    calculate_order_total(order)

    await db.delete(order_item)
    await db.commit()


# ============ Helper Functions ============

def calculate_order_total(order: Order) -> Decimal:
    """
    Пересчитать итоговую сумму заказа на основе текущих позиций.
    Возвращает новое значение total_amount.
    """
    items_total = sum(
        (item.unit_price or Decimal("0.00")) * item.quantity
        for item in order.items
    )
    order.total_amount = items_total + (order.shipping_cost or Decimal("0.00"))
    return order.total_amount


async def count_user_orders(user_id: int, db: AsyncSession) -> int:
    """
    Получить количество заказов пользователя через COUNT на уровне БД.
    Не загружает объекты в память.
    """
    result = await db.execute(
        select(func.count()).select_from(Order).where(Order.user_id == user_id)
    )
    return result.scalar_one()