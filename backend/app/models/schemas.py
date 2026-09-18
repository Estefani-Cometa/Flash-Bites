from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class IncomingMessage(BaseModel):
    tenant_id: int
    customer_id: int
    channel: Literal["web", "whatsapp", "cli"]
    text: str
    media_url: str | None = None
    timestamp: datetime


class OutgoingMessage(BaseModel):
    text: str
    media_url: str | None = None
    quick_replies: list[str] | None = None


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1)


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class ProductOut(BaseModel):
    id: str
    name: str
    price: float
    description: str


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None


class OrderItemInput(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: str
    items: list[OrderItemInput] = Field(min_length=1)


class OrderOut(BaseModel):
    id: str
    customer_id: str
    items: list[dict]
    total: float
    status: str
