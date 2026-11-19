from app.agents.intent_classifier import IntentClassifier
from app.agents.prompts import SYSTEM_PROMPT
from app.services.product_service import product_service
from app.services.rag_service import rag_service


class BusinessAIAgent:
    def chat(self, question: str) -> str:
        products = product_service.get_all()
        intent = IntentClassifier.classify(question, products)

        if intent == "greeting":
            return (
                "👋 ¡Hola! Bienvenido a Flash Bites.\n\n"
                "Puedo ayudarte con:\n\n"
                "🍔 Consultar productos\n"
                "🛒 Realizar pedidos\n"
                "🕒 Horarios\n"
                "🚚 Domicilios\n"
                "💳 Métodos de pago\n"
                "📄 Facturación"
            )

        if intent == "products":
            if not products:
                return "❌ No hay productos registrados."

            lines = ["🍔 MENÚ FLASH BITES\n"]
            for product in products:
                lines.append(
                    f"ID: {product['id']} · {product['name']}\n"
                    f"🗂 {product['category']}\n"
                    f"📝 {product['description']}\n"
                    f"🥗 Ingredientes: {product['ingredients']}\n"
                    f"💲 ${product['price']:,} COP\n"
                )
            lines.append("¿Cuál deseas ordenar? 😊")
            return "\n".join(lines)

        if intent == "order":
            product_names = "\n".join(
                f"• {product['name']} (ID: {product['id']}) — ${product['price']:,} COP"
                for product in products
            )
            return (
                "🛒 Claro. Indícame qué producto y cantidad deseas ordenar.\n\n"
                f"Productos disponibles:\n{product_names}"
            )

        if intent == "schedule":
            return (
                "🕒 Nuestro horario de atención es:\n\n"
                "📅 Lunes a Domingo\n"
                "⏰ 5:00 PM a 11:00 PM"
            )

        if intent == "delivery":
            return (
                "🚚 Sí realizamos domicilios.\n\n"
                "⏱ Tiempo estimado de entrega:\n"
                "30 a 45 minutos."
            )

        if intent == "payment":
            return (
                "💳 Recibimos los siguientes métodos de pago:\n\n"
                "✔ Efectivo\n"
                "✔ Nequi\n"
                "✔ Daviplata\n"
                "✔ Transferencia bancaria"
            )

        docs = rag_service.answer_question(question)
        if isinstance(docs, list):
            return "\n\n".join(doc.page_content for doc in docs).strip()

        return SYSTEM_PROMPT


agent = BusinessAIAgent()
