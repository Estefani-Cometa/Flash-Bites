from fastapi import APIRouter

from app.core.security import create_access_token
from app.models.schemas import RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest) -> TokenResponse:
    # TODO: persistir en DB real
    token = create_access_token(str(payload.email))
    return TokenResponse(token=token)
