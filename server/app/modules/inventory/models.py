from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["products.business_id", "products.id"],
            ondelete="RESTRICT",
            name="fk_inventory_business_product",
        ),
        ForeignKeyConstraint(
            ["business_id", "variant_id"],
            ["product_variants.business_id", "product_variants.id"],
            ondelete="RESTRICT",
            name="fk_inventory_business_variant",
        ),
        CheckConstraint("on_hand_qty >= 0", name="ck_inventory_on_hand_nonnegative"),
        CheckConstraint(
            "reorder_threshold IS NULL OR reorder_threshold >= 0",
            name="ck_inventory_reorder_threshold_nonnegative",
        ),
        CheckConstraint("version > 0", name="ck_inventory_version_positive"),
    )

    business_id: Mapped[UUID] = mapped_column(primary_key=True)
    product_id: Mapped[UUID] = mapped_column(primary_key=True)
    variant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    on_hand_qty: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    reorder_threshold: Mapped[Decimal | None] = mapped_column(Numeric(18, 3))
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    @property
    def quantity_available(self) -> Decimal:
        return self.on_hand_qty


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["inventory.business_id", "inventory.product_id"],
            ondelete="RESTRICT",
            name="fk_stock_movements_business_inventory",
        ),
        UniqueConstraint("business_id", "movement_key", name="uq_stock_movements_business_key"),
        CheckConstraint("quantity_delta <> 0", name="ck_stock_movements_delta_nonzero"),
        CheckConstraint("resulting_on_hand_qty >= 0", name="ck_stock_movements_result_nonnegative"),
        Index(
            "ix_stock_movements_business_product_created", "business_id", "product_id", "created_at"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    movement_key: Mapped[str] = mapped_column(String(160), nullable=False)
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    resulting_on_hand_qty: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class StockReservation(Base):
    __tablename__ = "stock_reservations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["inventory.business_id", "inventory.product_id"],
            ondelete="RESTRICT",
            name="fk_stock_reservations_business_product",
        ),
        ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="RESTRICT",
            name="fk_stock_reservations_order",
        ),
        UniqueConstraint(
            "business_id", "order_id", "product_id", name="uq_stock_reservations_order_product"
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'CONSUMED', 'RELEASED', 'EXPIRED')",
            name="ck_stock_reservations_status",
        ),
        CheckConstraint("quantity > 0", name="ck_stock_reservations_quantity_positive"),
        Index("ix_stock_reservations_business_order", "business_id", "order_id"),
        Index(
            "ix_stock_reservations_active_product",
            "business_id",
            "product_id",
            "status",
            "expires_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(nullable=False)
    order_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="ACTIVE")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
