import logging
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import AbstractContextManager
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent

from app.agents.agent_tools import build_tools_for
from app.core.config import settings
from app.db import normalize_database_url
from app.models.schemas import IncomingMessage, OutgoingMessage
from app.services.business_service import business_service

logger = logging.getLogger(__name__)

GEMINI_REQUEST_TIMEOUT_SECONDS = 20
AGENT_TIMEOUT_SECONDS = 40


SYSTEM_PROMPT = """
Eres el asistente vendedor de {business_name}. Hablas en español, con calidez y
naturalidad, como un vendedor humano profesional que conoce bien el negocio. Responde
de forma breve, como un mensaje real de chat. En la primera interacción preséntate
brevemente y pregunta el nombre del cliente de forma natural, sin hacerle repetir lo
que ya pidió; atiende su solicitud en el mismo mensaje. Usa el nombre después sin abusar.

Estás atendiendo únicamente al tenant_id {tenant_id}. Solo puedes responder sobre los
productos, servicios e información de ese negocio. Usa tools para consultar el menú,
el carrito y la información del negocio. Nunca inventes productos, precios,
promociones ni disponibilidad: todo dato factual debe venir de una tool. Si no tienes
la información, dilo explícitamente y ofrece escalar a un humano. Si la consulta no
está relacionada con el negocio, redirige amablemente sin responder el tema externo.

Si el cliente expresa hambre o pide una recomendación vaga, indaga con una sola
pregunta breve para entender su necesidad antes de recomendar. Si ya tienes suficiente
contexto, consulta el menú y ofrece una solución basada en datos reales.
Si un producto no existe o no está disponible, dilo con honestidad y usa la tool del
menú para ofrecer solo una o dos alternativas reales y relacionadas. Sé persuasivo,
respetuoso y nunca inventes una similitud, categoría o disponibilidad.
Puedes usar varias tools en el mismo turno si la solicitud combina acciones. No hagas
más de las acciones solicitadas y confirma claramente los cambios en el carrito.
Ofrece como máximo una sugerencia adicional de producto durante toda la conversación.
Si el cliente dice que no quiere nada más o que ya decidió, respétalo y no insistas.
Recuerda lo dicho en este hilo, evita repetir preguntas y adáptate si cambia de idea.
""".strip()


class BusinessAIAgent:
    def __init__(self):
        self._checkpointer: Any = None
        self._checkpointer_context: AbstractContextManager | None = None
        self.last_debug: dict[str, Any] = {"tools_called": [], "elapsed": 0.0}

    def _get_checkpointer(self):
        if self._checkpointer is not None:
            return self._checkpointer

        database_url = normalize_database_url(settings.database_url)
        if database_url.startswith("postgresql"):
            try:
                context = PostgresSaver.from_conn_string(database_url)
                self._checkpointer_context = context
                self._checkpointer = context.__enter__()
                self._checkpointer.setup()
                return self._checkpointer
            except Exception:
                logger.exception("No se pudo inicializar el checkpoint Postgres")
                if self._checkpointer_context:
                    self._checkpointer_context.__exit__(None, None, None)
                    self._checkpointer_context = None

        self._checkpointer = MemorySaver()
        return self._checkpointer

    def _build_graph(
        self,
        msg: IncomingMessage,
        tool_log: list[str],
        customer_name: str | None,
    ):
        model = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
            max_tokens=300,
            retries=1,
            request_timeout=GEMINI_REQUEST_TIMEOUT_SECONDS,
        )
        tools = build_tools_for(msg.tenant_id, msg.customer_id, tool_log.append)
        prompt = SYSTEM_PROMPT.format(
            business_name=settings.business_name,
            tenant_id=msg.tenant_id,
        ) + f"\n\nNombre conocido del cliente: {customer_name or 'desconocido'}."
        return create_react_agent(
            model,
            tools,
            prompt=prompt,
            checkpointer=self._get_checkpointer(),
        )

    @staticmethod
    def _message_text(message: Any) -> str:
        content = getattr(message, "content", message)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            ).strip()
        return str(content)

    def process_message(self, msg: IncomingMessage) -> OutgoingMessage:
        started = time.perf_counter()
        tool_log: list[str] = []
        try:
            customer_name = business_service.get_customer_name(
                msg.customer_id,
                msg.tenant_id,
            )
            if not customer_name and self._looks_like_name(msg.text):
                business_service.update_customer_name(
                    msg.customer_id,
                    msg.tenant_id,
                    msg.text,
                )
                customer_name = msg.text.strip()
            graph = self._build_graph(msg, tool_log, customer_name)
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(
                graph.invoke,
                {"messages": [{"role": "user", "content": msg.text}]},
                config={
                    "configurable": {
                        "thread_id": f"tenant:{msg.tenant_id}:customer:{msg.customer_id}"
                    },
                    "recursion_limit": 4,
                },
            )
            try:
                result = future.result(timeout=AGENT_TIMEOUT_SECONDS)
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
            messages = result.get("messages", [])
            text = self._message_text(messages[-1]) if messages else ""
            if not text:
                text = "No pude generar una respuesta en este momento."
            return OutgoingMessage(text=text)
        except Exception:
            logger.exception("Error en agente LangGraph")
            return OutgoingMessage(
                text="Estoy teniendo un problema técnico en este momento, ¿puedes intentar de nuevo en un momento?"
            )
        finally:
            self.last_debug = {
                "tools_called": tool_log,
                "elapsed": round(time.perf_counter() - started, 3),
            }

    @staticmethod
    def _looks_like_name(text: str) -> bool:
        words = text.strip().split()
        excluded = {
            "hola",
            "buenas",
            "menu",
            "productos",
            "horario",
            "carrito",
            "pedido",
        }
        return (
            1 <= len(words) <= 3
            and all(word.isalpha() for word in words)
            and not any(word.lower() in excluded for word in words)
        )


agent = BusinessAIAgent()
