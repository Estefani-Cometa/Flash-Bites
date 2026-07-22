from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.agents.ai_agent import agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
def chat(
    payload: dict | None = Body(None),
    current_user: dict = Depends(get_current_user),
) -> dict:

    message = payload.get("message") if isinstance(payload, dict) else payload

    if not isinstance(message, str) or not message.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="message is required",
        )

    answer = agent.chat(message)

    return {
        "reply": answer
    }