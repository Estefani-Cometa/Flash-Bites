from typing import Any

from app.services.product_service import product_service


class BusinessService:
    """Servicio de negocio con reglas básicas del dominio."""

    def __init__(self) -> None:
        self.customers: list[dict[str, Any]] = []
        self.orders: list[dict[str, Any]] = []

    def list_products(self) -> list[dict[str, Any]]:
        return product_service.get_all()

    def register_customer(self, payload: dict[str, Any]) -> dict[str, Any]:
        customer = {"id": f"cust-{len(self.customers) + 1}", **payload}
        self.customers.append(customer)
        return customer

    def create_order(self, customer_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
        total = sum(
            self._find_product(item["product_id"])["price"] * item["quantity"]
            for item in items
        )
        order = {
            "id": f"order-{len(self.orders) + 1}",
            "customer_id": customer_id,
            "items": items,
            "total": round(total, 2),
            "status": "pending",
        }
        self.orders.append(order)
        return order

    def _find_product(self, product_id: str) -> dict[str, str | int]:
        return product_service.get_by_id(product_id)

    def list_orders(self) -> list[dict[str, Any]]:
        return self.orders


business_service = BusinessService()
