from typing import Any


class BusinessService:
    """Servicio de negocio con reglas básicas del dominio."""

    def __init__(self) -> None:
        self.products = [
            {"id": "prod-1", "name": "Café Premium", "price": 4.5, "description": "Café de especialidad"},
            {"id": "prod-2", "name": "Té Verde", "price": 3.2, "description": "Té orgánico"},
            {"id": "prod-3", "name": "Empanada", "price": 2.8, "description": "Empanada de carne"},
        ]
        self.customers: list[dict[str, Any]] = []
        self.orders: list[dict[str, Any]] = []

    def list_products(self) -> list[dict[str, Any]]:
        return self.products

    def register_customer(self, payload: dict[str, Any]) -> dict[str, Any]:
        customer = {"id": f"cust-{len(self.customers) + 1}", **payload}
        self.customers.append(customer)
        return customer

    def create_order(self, customer_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
        total = sum(self._find_product(item["product_id"])["price"] * item["quantity"] for item in items)
        order = {
            "id": f"order-{len(self.orders) + 1}",
            "customer_id": customer_id,
            "items": items,
            "total": round(total, 2),
            "status": "pending",
        }
        self.orders.append(order)
        return order

    def _find_product(self, product_id: str) -> dict[str, Any]:
        for product in self.products:
            if product["id"] == product_id:
                return product
        raise ValueError("Product not found")

    def list_orders(self) -> list[dict[str, Any]]:
        return self.orders


business_service = BusinessService()
