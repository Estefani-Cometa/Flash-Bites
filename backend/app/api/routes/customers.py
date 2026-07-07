from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.schemas import CustomerCreate
from app.services.business_service import business_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", status_code=201)
def create_customer(payload: CustomerCreate, current_user: dict = Depends(get_current_user)) -> dict:
    return business_service.register_customer(payload.model_dump())
