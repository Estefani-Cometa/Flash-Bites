from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


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
    quantity: int


class OrderCreate(BaseModel):
    customer_id: str
    items: list[OrderItemInput]


class OrderOut(BaseModel):
    id: str
    customer_id: str
    items: list[dict]
    total: float
    status: str
