from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.schemas import OrderCreate, OrderOut
from app.services.business_service import business_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(payload: OrderCreate, current_user: dict = Depends(get_current_user)) -> OrderOut:
    try:
        order = business_service.create_order(payload.customer_id, [item.model_dump() for item in payload.items])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return OrderOut(**order)


@router.get("", response_model=list[OrderOut])
def list_orders(current_user: dict = Depends(get_current_user)) -> list[OrderOut]:
    return [OrderOut(**order) for order in business_service.list_orders()]
