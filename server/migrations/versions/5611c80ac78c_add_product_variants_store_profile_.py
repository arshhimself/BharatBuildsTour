"""add product variants store profile product media and checkout sessions

Revision ID: 5611c80ac78c
Revises: e5b4a228093f
Create Date: 2026-09-20 04:13:53.870718

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5611c80ac78c"  # pragma: allowlist secret
down_revision: str | Sequence[str] | None = "e5b4a228093f"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_variants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("size", sa.String(length=32), nullable=True),
        sa.Column("color", sa.String(length=32), nullable=True),
        sa.Column("price_override_paise", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["products.business_id", "products.id"],
            ondelete="CASCADE",
            name="fk_product_variants_business_product",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "id", name="uq_product_variants_business_id_id"),
        sa.UniqueConstraint("business_id", "sku", name="uq_product_variants_business_sku"),
    )
    op.create_index(
        "ix_product_variants_business_product",
        "product_variants",
        ["business_id", "product_id"],
        unique=False,
    )

    op.create_table(
        "product_media",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("media_url", sa.String(length=1024), nullable=False),
        sa.Column("media_type", sa.String(length=32), server_default="image", nullable=False),
        sa.Column("position", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["products.business_id", "products.id"],
            ondelete="CASCADE",
            name="fk_product_media_business_product",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "id", name="uq_product_media_business_id_id"),
    )
    op.create_index(
        "ix_product_media_business_product",
        "product_media",
        ["business_id", "product_id"],
        unique=False,
    )

    op.create_table(
        "store_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("store_type", sa.String(length=128), nullable=True),
        sa.Column("address_line", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("support_number", sa.String(length=32), nullable=True),
        sa.Column("opening_hours", sa.String(length=255), nullable=True),
        sa.Column("delivery_info", sa.String(length=512), nullable=True),
        sa.Column("return_policy", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", name="uq_store_profiles_business_id"),
    )

    op.create_table(
        "checkout_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'completed', 'expired')", name="ck_checkout_sessions_status"
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "token_hash", name="uq_checkout_sessions_token_hash"),
    )

    op.add_column("inventory", sa.Column("variant_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_inventory_business_variant",
        "inventory",
        "product_variants",
        ["business_id", "variant_id"],
        ["business_id", "id"],
        ondelete="RESTRICT",
    )

    op.add_column("cart_items", sa.Column("variant_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_cart_items_variant",
        "cart_items",
        "product_variants",
        ["variant_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("order_items", sa.Column("variant_id", sa.Uuid(), nullable=True))
    op.add_column("order_items", sa.Column("size_snapshot", sa.String(length=32), nullable=True))
    op.add_column("order_items", sa.Column("color_snapshot", sa.String(length=32), nullable=True))
    op.create_foreign_key(
        "fk_order_items_variant",
        "order_items",
        "product_variants",
        ["variant_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_order_items_variant", "order_items", type_="foreignkey")
    op.drop_column("order_items", "color_snapshot")
    op.drop_column("order_items", "size_snapshot")
    op.drop_column("order_items", "variant_id")

    op.drop_constraint("fk_cart_items_variant", "cart_items", type_="foreignkey")
    op.drop_column("cart_items", "variant_id")

    op.drop_constraint("fk_inventory_business_variant", "inventory", type_="foreignkey")
    op.drop_column("inventory", "variant_id")

    op.drop_table("checkout_sessions")
    op.drop_table("store_profiles")
    op.drop_table("product_media")
    op.drop_table("product_variants")
