from fastapi import APIRouter

from app.models.schemas import ProductOut
from app.services.business_service import business_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=dict)
def list_products() -> dict:
    return {"items": [ProductOut(**product).model_dump() for product in business_service.list_products()]}
