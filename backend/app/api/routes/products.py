from fastapi import APIRouter

from app.models.schemas import ProductListOut
from app.services.business_service import business_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListOut)
def list_products() -> ProductListOut:
    return ProductListOut(items=business_service.list_products())
