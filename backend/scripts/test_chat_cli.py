import logging
from datetime import datetime, timezone

from app.agents.ai_agent import agent
from app.api.routes.chat import business_service
from app.core.config import settings
from app.db import initialize_database
from app.models.schemas import IncomingMessage
from app.services.product_service import product_service


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    initialize_database()
    product_service.import_from_csv_if_empty()
    print("Flash-Bites CLI. Escribe /cliente <telefono> para cambiar de cliente o /salir para terminar.")
    phone = input("Telefono simulado: ").strip()
    if not phone or phone.lower() in {"salir", "/salir"}:
        return

    customer_id = business_service.get_or_create_customer(
        user_id=f"cli:{phone}",
        phone=phone,
    )
    print(f"Cliente activo: {phone}. Puedes enviar varios mensajes seguidos.")

    while True:
        text = input("Tu: ").strip()
        if text.lower() in {"salir", "/salir"}:
            break
        if not text:
            continue

        if text.lower().startswith("/cliente"):
            new_phone = text[len("/cliente"):].strip()
            if not new_phone:
                print("Uso: /cliente <telefono>")
                continue
            phone = new_phone
            customer_id = business_service.get_or_create_customer(
                user_id=f"cli:{phone}",
                phone=phone,
            )
            print(f"Cliente activo: {phone}.")
            continue

        incoming = IncomingMessage(
            tenant_id=settings.tenant_id,
            customer_id=customer_id,
            channel="cli",
            text=text,
            timestamp=datetime.now(timezone.utc),
        )
        response = agent.process_message(incoming)
        debug = agent.last_debug
        print(
            f"[debug] tools_called={debug['tools_called']} "
            f"tiempo={debug['elapsed']}s"
        )
        print(f"Asistente: {response.text}\n")


if __name__ == "__main__":
    main()
