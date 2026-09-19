from __future__ import annotations

"""Database models for Social Media Agent & Instagram Publishing."""

from datetime import datetime
from uuid import UUID, uuid4

from typing import Optional

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SocialPost(Base):
    __tablename__ = "social_posts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    platform: Mapped[str] = mapped_column(String(32), nullable=False, default="instagram")
    platform_account_id: Mapped[Optional[str]] = mapped_column(String(128))
    media_id: Mapped[Optional[str]] = mapped_column(String(128))
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PUBLISHED")
    error: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
