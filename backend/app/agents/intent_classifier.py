class IntentClassifier:

    @staticmethod
    def classify(message: str) -> str:

        text = message.lower()

        # saludo
        if any(word in text for word in [
            "hola",
            "buenas",
            "buenos días",
            "buenas tardes",
            "buenas noches"
        ]):
            return "greeting"

        # productos
        if any(word in text for word in [
            "producto",
            "productos",
            "menu",
            "menú",
            "hamburguesa",
            "perro",
            "salchipapa",
            "salchiqueso",
            "precio"
        ]):
            return "products"

        # pedidos
        if any(word in text for word in [
            "pedido",
            "orden",
            "comprar",
            "quiero",
            "llevar"
        ]):
            return "order"

        # horario
        if any(word in text for word in [
            "horario",
            "hora",
            "abren",
            "cierran"
        ]):
            return "schedule"

        # domicilio
        if any(word in text for word in [
            "domicilio",
            "envío",
            "envio",
            "entrega"
        ]):
            return "delivery"

        # pago
        if any(word in text for word in [
            "pago",
            "nequi",
            "daviplata",
            "transferencia",
            "efectivo"
        ]):
            return "payment"

        return "rag"