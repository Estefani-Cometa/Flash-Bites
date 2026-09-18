from typing import Any

from sqlalchemy import select

from app.core.config import settings
from app.db import SessionLocal
from app.db_models import Customer, Order
from app.services.product_service import product_service


class BusinessService:
    """Servicio de negocio con reglas básicas del dominio."""

    def __init__(self) -> None:
        pass

    def list_products(self) -> list[dict[str, Any]]:
        return [
            {
                "id": str(product["id"]),
                "name": product["nombre"],
                "price": float(product["precio"]),
                "description": product.get("descripcion", ""),
            }
            for product in product_service.get_all()
        ]

    def register_customer(self, payload: dict[str, Any], user_id: str) -> dict[str, Any]:
        with SessionLocal.begin() as db:
            customer = Customer(
                tenant_id=settings.tenant_id,
                user_id=user_id,
                telefono=payload.get("phone"),
                nombre=payload["name"],
                email=payload.get("email"),
            )
            db.add(customer)
            db.flush()
            return {
                "id": f"cust-{customer.id}",
                "name": customer.nombre,
                "email": customer.email,
                "phone": customer.telefono,
            }

    def get_or_create_customer(self, user_id: str, phone: str | None = None) -> int:
        with SessionLocal.begin() as db:
            customer = db.scalar(
                select(Customer).where(
                    Customer.tenant_id == settings.tenant_id,
                    Customer.user_id == user_id,
                ).order_by(Customer.id)
            )
            if customer is None:
                customer = Customer(
                    tenant_id=settings.tenant_id,
                    user_id=user_id,
                    telefono=phone,
                    nombre="",
                    email=user_id if "@" in user_id else None,
                )
                db.add(customer)
                db.flush()
            return customer.id

    def get_customer_name(self, customer_id: int, tenant_id: int) -> str | None:
        with SessionLocal() as db:
            customer = db.scalar(
                select(Customer).where(
                    Customer.id == customer_id,
                    Customer.tenant_id == tenant_id,
                )
            )
            return customer.nombre.strip() if customer and customer.nombre else None

    def update_customer_name(self, customer_id: int, tenant_id: int, name: str) -> None:
        with SessionLocal.begin() as db:
            customer = db.scalar(
                select(Customer).where(
                    Customer.id == customer_id,
                    Customer.tenant_id == tenant_id,
                )
            )
            if customer is not None:
                customer.nombre = name.strip()

    def create_order(
        self,
        customer_id: str,
        items: list[dict[str, Any]],
        user_id: str,
    ) -> dict[str, Any]:
        if not items:
            raise ValueError("La lista de items del pedido no puede estar vacía")

        for item in items:
            quantity = item.get("quantity")
            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("La cantidad debe ser un entero positivo mayor a 0")

        with SessionLocal.begin() as db:
            customer = self._get_customer(db, customer_id, user_id)
            total = sum(
                self._find_product(item["product_id"])["price"] * item["quantity"]
                for item in items
            )
            order_record = Order(
                tenant_id=settings.tenant_id,
                customer_id=customer.id,
                items=items,
                estado="pending",
            )
            db.add(order_record)
            db.flush()
            return {
                "id": f"order-{order_record.id}",
                "customer_id": f"cust-{customer.id}",
                "items": items,
                "total": round(total, 2),
                "status": order_record.estado,
            }

    def _get_customer(self, db, customer_id: str, user_id: str) -> Customer:
        try:
            numeric_id = int(customer_id.removeprefix("cust-"))
        except ValueError as exc:
            raise ValueError("El customer_id no es válido") from exc

        customer = db.scalar(
            select(Customer).where(
                Customer.id == numeric_id,
                Customer.tenant_id == settings.tenant_id,
                Customer.user_id == user_id,
            )
        )
        if customer is None:
            raise ValueError("El cliente no pertenece al usuario autenticado")
        return customer

    def _find_product(self, product_id: str) -> dict[str, Any]:
        for product in self.list_products():
            if product["id"] == str(product_id):
                return product
        raise ValueError(f"Producto {product_id} no encontrado")

    def list_orders(self, user_id: str) -> list[dict[str, Any]]:
        with SessionLocal() as db:
            records = db.scalars(
                select(Order)
                .join(Customer, Customer.id == Order.customer_id)
                .where(
                    Order.tenant_id == settings.tenant_id,
                    Customer.tenant_id == settings.tenant_id,
                    Customer.user_id == user_id,
                )
                .order_by(Order.id)
            ).all()
            return [
                {
                    "id": f"order-{order.id}",
                    "customer_id": f"cust-{order.customer_id}",
                    "items": order.items,
                    "total": round(
                        sum(
                            self._find_product(item["product_id"])["price"] * item["quantity"]
                            for item in order.items
                        ),
                        2,
                    ),
                    "status": order.estado,
                }
                for order in records
            ]


business_service = BusinessService()
