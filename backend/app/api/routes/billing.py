from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.services.business_service import business_service

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/invoice/{order_id}")
def generate_invoice(order_id: str, current_user: dict = Depends(get_current_user)) -> Response:
    order = next((item for item in business_service.list_orders() if item["id"] == order_id), None)
    if not order:
        return Response(status_code=404, content="Order not found")
    content = f"Factura simulada para pedido {order_id}\nTotal: {order['total']}"
    return StreamingResponse(iter([content]), media_type="application/pdf")
