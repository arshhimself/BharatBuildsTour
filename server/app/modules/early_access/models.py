from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EarlyAccessLead(Base):
    __tablename__ = "early_access_leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    business_type: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    about_business: Mapped[str] = mapped_column(Text, nullable=False)
    daily_whatsapp_orders: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    source: Mapped[str] = mapped_column(String(100), nullable=False, default="website_early_access")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="new")
    payment_status: Mapped[str] = mapped_column(String(50), nullable=False, default="not_started")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
