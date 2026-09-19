from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InvoiceSequence(Base):
    __tablename__ = "invoice_sequences"
    __table_args__ = (
        CheckConstraint("calendar_year BETWEEN 2000 AND 9999", name="ck_invoice_sequences_year"),
        CheckConstraint("next_value > 0", name="ck_invoice_sequences_next_positive"),
    )

    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="RESTRICT"), primary_key=True
    )
    calendar_year: Mapped[int] = mapped_column(Integer, primary_key=True)
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "quote_id", "quote_version", "run_id"],
            ["quotes.business_id", "quotes.id", "quotes.quote_version", "quotes.run_id"],
            ondelete="RESTRICT",
            name="fk_invoices_business_quote_version_run",
        ),
        ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="RESTRICT",
            name="fk_invoices_order",
        ),
        ForeignKeyConstraint(
            ["business_id", "payment_id"],
            ["payments.business_id", "payments.id"],
            ondelete="RESTRICT",
            name="fk_invoices_business_payment",
        ),
        UniqueConstraint("business_id", "payment_id", name="uq_invoices_business_payment"),
        UniqueConstraint("business_id", "quote_id", name="uq_invoices_business_quote"),
        UniqueConstraint("business_id", "order_id", name="uq_invoices_business_order"),
        UniqueConstraint("business_id", "invoice_number", name="uq_invoices_business_number"),
        CheckConstraint(
            "length(trim(run_id)) > 0 OR run_id IS NULL", name="ck_invoices_run_nonempty"
        ),
        CheckConstraint(
            "quote_version > 0 OR quote_version IS NULL", name="ck_invoices_quote_version_positive"
        ),
        CheckConstraint(
            "(quote_id IS NOT NULL AND order_id IS NULL) OR (quote_id IS NULL AND order_id IS NOT NULL)",
            name="ck_invoices_quote_or_order",
        ),
        CheckConstraint("status IN ('PENDING_ARTIFACT', 'GENERATED')", name="ck_invoices_status"),
        CheckConstraint("currency = 'INR'", name="ck_invoices_currency_inr"),
        CheckConstraint("total_paise > 0", name="ck_invoices_total_positive"),
        CheckConstraint(
            "invoice_number ~ '^INV-[0-9]{4}-[0-9]{6}$'",
            name="ck_invoices_number_format",
        ),
        CheckConstraint(
            "status <> 'GENERATED' OR (artifact_key IS NOT NULL AND "
            "artifact_sha256 IS NOT NULL AND generated_at IS NOT NULL)",
            name="ck_invoices_generated_artifact",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(nullable=False)
    run_id: Mapped[str | None] = mapped_column(String(160))
    quote_id: Mapped[UUID | None] = mapped_column()
    quote_version: Mapped[int | None] = mapped_column(Integer)
    order_id: Mapped[UUID | None] = mapped_column()
    payment_id: Mapped[UUID] = mapped_column(nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default="PENDING_ARTIFACT"
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="INR")
    total_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    artifact_key: Mapped[str | None] = mapped_column(String(500))
    artifact_sha256: Mapped[str | None] = mapped_column(String(64))
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
