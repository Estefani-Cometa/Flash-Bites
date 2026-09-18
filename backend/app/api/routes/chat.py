from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.agents.ai_agent import agent
from app.api.deps import get_current_user
from app.core.config import settings
from app.models.schemas import IncomingMessage
from app.services.business_service import business_service


router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("")
def chat(
    payload: dict | None = Body(None),
    current_user: dict = Depends(get_current_user),
) -> dict:

    message = (
        payload.get("message")
        if isinstance(payload, dict)
        else payload
    )

    if not isinstance(message, str) or not message.strip():

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="message is required",
        )

    customer_id = business_service.get_or_create_customer(current_user["email"])
    incoming = IncomingMessage(
        tenant_id=settings.tenant_id,
        customer_id=customer_id,
        channel="web",
        text=message,
        timestamp=datetime.now(timezone.utc),
    )
    answer = agent.process_message(incoming)

    return {
        "reply": answer.text
    }