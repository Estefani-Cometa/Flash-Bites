"""Create multi-tenant schema.

Revision ID: 0001_initial_schema
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("tenants", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nombre_negocio", sa.String(150), nullable=False), sa.Column("telefono_whatsapp", sa.String(30)), sa.Column("plan", sa.String(50), nullable=False), sa.Column("activo", sa.Boolean(), nullable=False), sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("tenant_documents", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("tipo", sa.String(30), nullable=False), sa.Column("contenido", sa.Text(), nullable=False), sa.Column("url_imagen", sa.String(500)), sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Index("ix_tenant_documents_tenant_id", "tenant_id"))
    op.create_table("products", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("nombre", sa.String(150), nullable=False), sa.Column("precio", sa.Integer(), nullable=False), sa.Column("descripcion", sa.Text(), nullable=False), sa.Column("imagen_url", sa.String(500)), sa.Column("disponible", sa.Boolean(), nullable=False), sa.Index("ix_products_tenant_id", "tenant_id"))
    op.create_table("customers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("user_id", sa.String(320), nullable=False), sa.Column("telefono", sa.String(30)), sa.Column("nombre", sa.String(150), nullable=False), sa.Column("email", sa.String(320)), sa.Index("ix_customers_tenant_id", "tenant_id"), sa.Index("ix_customers_user_id", "user_id"))
    item_type = sa.JSON()
    op.create_table("orders", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False), sa.Column("items", item_type, nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Index("ix_orders_tenant_id", "tenant_id"), sa.Index("ix_orders_customer_id", "customer_id"))
    op.create_table("conversations", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False), sa.Column("historial", item_type, nullable=False), sa.Column("carrito", item_type, nullable=False), sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Index("ix_conversations_tenant_id", "tenant_id"), sa.Index("ix_conversations_customer_id", "customer_id"))
    op.execute(sa.text("INSERT INTO tenants (id, nombre_negocio, plan, activo) VALUES (1, 'Flash Bites', 'mvp', true)"))


def downgrade() -> None:
    op.drop_table("conversations")
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_table("products")
    op.drop_table("tenant_documents")
    op.drop_table("tenants")
