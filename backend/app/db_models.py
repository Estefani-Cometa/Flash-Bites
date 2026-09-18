from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


JsonType = JSON().with_variant(JSONB, "postgresql")


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_negocio: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono_whatsapp: Mapped[str | None] = mapped_column(String(30))
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="mvp")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TenantDocument(Base):
    __tablename__ = "tenant_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    url_imagen: Mapped[str | None] = mapped_column(String(500))
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    precio: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, default="")
    imagen_url: Mapped[str | None] = mapped_column(String(500))
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    telefono: Mapped[str | None] = mapped_column(String(30))
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    items: Mapped[list[dict[str, Any]]] = mapped_column(JsonType, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    historial: Mapped[list[dict[str, str]]] = mapped_column(JsonType, nullable=False, default=list)
    carrito: Mapped[list[dict[str, Any]]] = mapped_column(JsonType, nullable=False, default=list)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
