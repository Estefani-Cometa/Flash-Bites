from collections.abc import Sequence


class IntentClassifier:
    @staticmethod
    def classify(
        message: str,
        products: Sequence[dict[str, str | int]] = (),
    ) -> str:
        text = message.casefold()

        if any(
            word in text
            for word in (
                "hola",
                "buenas",
                "buenos días",
                "buenas tardes",
                "buenas noches",
            )
        ):
            return "greeting"

        if any(
            word in text
            for word in ("pedido", "orden", "comprar", "quiero", "llevar")
        ):
            return "order"

        product_terms = (
            "producto",
            "productos",
            "menu",
            "menú",
            "precio",
            "ingredientes",
        )
        product_tokens = {
            token
            for product in products
            for field in ("name", "category")
            for token in str(product.get(field, "")).casefold().split()
            if len(token) >= 4
        }
        if any(term in text for term in product_terms) or any(
            token in text for token in product_tokens
        ):
            return "products"

        if any(word in text for word in ("horario", "hora", "abren", "cierran")):
            return "schedule"

        if any(word in text for word in ("domicilio", "envío", "envio", "entrega")):
            return "delivery"

        if any(
            word in text
            for word in ("pago", "nequi", "daviplata", "transferencia", "efectivo")
        ):
            return "payment"

        return "rag"
