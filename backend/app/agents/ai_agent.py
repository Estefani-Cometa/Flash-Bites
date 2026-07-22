from app.services.rag_service import rag_service
from app.services.product_service import product_service

from app.agents.prompts import SYSTEM_PROMPT
from app.agents.intent_classifier import IntentClassifier


class BusinessAIAgent:

    def chat(self, question: str) -> str:

        intent = IntentClassifier.classify(question)

        # ======================================================
        # SALUDO
        # ======================================================

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

        # ======================================================
        # PRODUCTOS
        # ======================================================

        if intent == "products":

            productos = product_service.get_all()

            if not productos:

                return "❌ No hay productos registrados."

            respuesta = "🍔 MENÚ FLASH BITES\n\n"

            for producto in productos:

                respuesta += (
                    f"🍔 {producto['nombre']}\n"
                    f"📝 {producto['descripcion']}\n"
                    f"💲 ${producto['precio']:,}\n\n"
                )

            respuesta += "¿Cuál deseas ordenar? 😊"

            return respuesta

        # ======================================================
        # PEDIDOS
        # ======================================================

        if intent == "order":

            return (
                "🛒 Claro.\n\n"
                "Indícame qué producto deseas ordenar.\n\n"
                "Por ejemplo:\n\n"
                "• Hamburguesa Clásica\n"
                "• Hamburguesa Doble\n"
                "• Hamburguesa BBQ\n"
                "• Perro Caliente\n"
                "• Salchipapa"
            )

        # ======================================================
        # HORARIOS
        # ======================================================

        if intent == "schedule":

            return (
                "🕒 Nuestro horario de atención es:\n\n"
                "📅 Lunes a Domingo\n"
                "⏰ 5:00 PM a 11:00 PM"
            )

        # ======================================================
        # DOMICILIOS
        # ======================================================

        if intent == "delivery":

            return (
                "🚚 Sí realizamos domicilios.\n\n"
                "⏱ Tiempo estimado de entrega:\n"
                "30 a 45 minutos."
            )

        # ======================================================
        # PAGOS
        # ======================================================

        if intent == "payment":

            return (
                "💳 Recibimos los siguientes métodos de pago:\n\n"
                "✔ Efectivo\n"
                "✔ Nequi\n"
                "✔ Daviplata\n"
                "✔ Transferencia bancaria"
            )

        # ======================================================
        # CONSULTAS GENERALES (RAG)
        # ======================================================

        docs = rag_service.answer_question(question)

        if isinstance(docs, list):

            respuesta = ""

            for doc in docs:

                respuesta += doc.page_content
                respuesta += "\n\n"

            return respuesta.strip()

        return SYSTEM_PROMPT


agent = BusinessAIAgent()