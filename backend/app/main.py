from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.billing import router as billing_router
from app.api.routes.chat import router as chat_router
from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.products import router as products_router
from app.core.config import settings
from app.db import initialize_database
from app.services.product_service import product_service

app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/docs", redoc_url="/redoc")
allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(products_router, prefix=settings.api_v1_prefix)
app.include_router(customers_router, prefix=settings.api_v1_prefix)
app.include_router(orders_router, prefix=settings.api_v1_prefix)
app.include_router(billing_router, prefix=settings.api_v1_prefix)
app.include_router(chat_router, prefix=settings.api_v1_prefix)

initialize_database()
product_service.import_from_csv_if_empty()
