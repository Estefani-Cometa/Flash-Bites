from sqlalchemy import select

from app.db import SessionLocal
from app.db_models import Conversation, Customer


class ShoppingCart:
    """Carrito persistido como JSON dentro de conversations."""

    def _get_conversation(self, db, tenant_id: int, customer_id: int) -> Conversation:
        customer = db.scalar(
            select(Customer).where(
                Customer.tenant_id == tenant_id,
                Customer.id == customer_id,
            )
        )
        if customer is None:
            raise ValueError("El cliente no existe en el tenant")
        conversation = db.scalar(
            select(Conversation).where(
                Conversation.tenant_id == tenant_id,
                Conversation.customer_id == customer.id,
            )
        )
        if conversation is None:
            conversation = Conversation(tenant_id=tenant_id, customer_id=customer.id, historial=[], carrito=[])
            db.add(conversation)
            db.flush()
        return conversation

    def add_product(self, tenant_id: int, customer_id: int, product: dict, quantity: int = 1):
        with SessionLocal.begin() as db:
            conversation = self._get_conversation(db, tenant_id, customer_id)
            cart = list(conversation.carrito or [])
            for item in cart:
                if item["id"] == product["id"]:
                    item["cantidad"] += quantity
                    conversation.carrito = cart
                    return
            cart.append({"id": product["id"], "nombre": product["nombre"], "precio": product["precio"], "cantidad": quantity})
            conversation.carrito = cart

    def remove_product(self, tenant_id: int, customer_id: int, product_id: int) -> bool:
        with SessionLocal.begin() as db:
            conversation = self._get_conversation(db, tenant_id, customer_id)
            cart = list(conversation.carrito or [])
            updated = [item for item in cart if item["id"] != product_id]
            conversation.carrito = updated
            return len(updated) != len(cart)

    def clear(self, tenant_id: int, customer_id: int):
        with SessionLocal.begin() as db:
            self._get_conversation(db, tenant_id, customer_id).carrito = []

    def get_items(self, tenant_id: int, customer_id: int) -> list[dict]:
        with SessionLocal() as db:
            return list(self._get_conversation(db, tenant_id, customer_id).carrito or [])

    def total(self, tenant_id: int, customer_id: int):
        return sum(item["precio"] * item["cantidad"] for item in self.get_items(tenant_id, customer_id))

    def summary(self, tenant_id: int, customer_id: int):
        cart = self.get_items(tenant_id, customer_id)
        if not cart:
            return "🛒 El carrito está vacío."
        text = "🛒 Pedido actual:\n\n"
        for item in cart:
            text += f"• {item['nombre']}\nCantidad: {item['cantidad']}\nSubtotal: ${item['precio'] * item['cantidad']:,}\n\n"
        return text + f"TOTAL: ${self.total(tenant_id, customer_id):,}"


shopping_cart = ShoppingCart()
