import asyncio
import unittest
from pathlib import Path

from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import enable_sqlite_foreign_keys, get_db
from app.models.cart_item import CartItem
from main import app


class CartApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.db_path = Path("test_app.db")
        if self.db_path.exists():
            self.db_path.unlink()

        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{self.db_path}",
            future=True,
        )
        enable_sqlite_foreign_keys(self.engine)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        async def override_get_db():
            async with self.session_factory() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        self.client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()
        app.dependency_overrides.clear()
        await self.engine.dispose()

        if self.db_path.exists():
            self.db_path.unlink()

    async def _create_product(
        self,
        *,
        title: str = "Product",
        price: str = "19.99",
        inventory: int = 10,
    ) -> int:
        response = await self.client.post(
            "/api/products",
            json={
                "title": title,
                "description": "Test item",
                "price": price,
                "inventory": inventory,
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["id"]

    async def _create_cart(self) -> dict:
        response = await self.client.post("/api/carts")
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    async def test_cart_requires_valid_token(self) -> None:
        cart = await self._create_cart()

        response = await self.client.get(f"/api/carts/{cart['id']}")
        self.assertEqual(response.status_code, 403, response.text)

        response = await self.client.get(
            f"/api/carts/{cart['id']}",
            headers={"X-Cart-Token": "wrong-token"},
        )
        self.assertEqual(response.status_code, 403, response.text)

        response = await self.client.get(
            f"/api/carts/{cart['id']}",
            headers={"X-Cart-Token": cart["session_token"]},
        )
        self.assertEqual(response.status_code, 200, response.text)

    async def test_cannot_delete_product_while_it_is_in_cart(self) -> None:
        product_id = await self._create_product()
        cart = await self._create_cart()
        headers = {"X-Cart-Token": cart["session_token"]}

        response = await self.client.post(
            f"/api/carts/{cart['id']}/items",
            json={"product_id": product_id, "quantity": 1},
            headers=headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        response = await self.client.delete(f"/api/products/{product_id}")
        self.assertEqual(response.status_code, 409, response.text)

    async def test_product_can_be_deleted_after_cart_is_cleared(self) -> None:
        product_id = await self._create_product()
        cart = await self._create_cart()
        headers = {"X-Cart-Token": cart["session_token"]}

        response = await self.client.post(
            f"/api/carts/{cart['id']}/items",
            json={"product_id": product_id, "quantity": 1},
            headers=headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        response = await self.client.delete(
            f"/api/carts/{cart['id']}/items",
            headers=headers,
        )
        self.assertEqual(response.status_code, 204, response.text)

        response = await self.client.delete(f"/api/products/{product_id}")
        self.assertEqual(response.status_code, 204, response.text)

    async def test_parallel_add_item_keeps_single_cart_row(self) -> None:
        product_id = await self._create_product(inventory=3)
        cart = await self._create_cart()
        headers = {"X-Cart-Token": cart["session_token"]}

        async def add_one():
            return await self.client.post(
                f"/api/carts/{cart['id']}/items",
                json={"product_id": product_id, "quantity": 1},
                headers=headers,
            )

        first_response, second_response = await asyncio.gather(add_one(), add_one())
        self.assertEqual(first_response.status_code, 200, first_response.text)
        self.assertEqual(second_response.status_code, 200, second_response.text)

        async with self.session_factory() as session:
            result = await session.execute(
                select(CartItem).where(
                    CartItem.cart_id == cart["id"],
                    CartItem.product_id == product_id,
                )
            )
            items = list(result.scalars().all())

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].quantity, 2)

    async def test_cart_response_contains_product_snapshot_and_totals(self) -> None:
        product_id = await self._create_product(title="Lamp", price="99.50", inventory=4)
        cart = await self._create_cart()
        headers = {"X-Cart-Token": cart["session_token"]}

        response = await self.client.post(
            f"/api/carts/{cart['id']}/items",
            json={"product_id": product_id, "quantity": 2},
            headers=headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        payload = response.json()
        self.assertEqual(payload["items_count"], 2)
        self.assertEqual(payload["total_amount"], "199.00")
        self.assertEqual(payload["items"][0]["product"]["title"], "Lamp")
        self.assertEqual(payload["items"][0]["line_total"], "199.00")
