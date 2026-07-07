from fastapi import APIRouter, Body, Depends

from app.api.deps import get_current_user
from app.services.rag_service import rag_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
def chat(message: str = Body(...), current_user: dict = Depends(get_current_user)) -> dict:
    answer = rag_service.answer_question(message)
    return {"reply": answer}
