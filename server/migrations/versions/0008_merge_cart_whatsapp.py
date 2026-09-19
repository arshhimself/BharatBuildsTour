"""Merge legacy guided-cart and WhatsApp-commerce branches.

Revision ID: 0008_merge_cart_whatsapp
Revises: 0006_buyer_cart_sessions, 0007_buyers_unique_whatsapp
"""

from collections.abc import Sequence

revision = "0008_merge_cart_whatsapp"
down_revision: str | Sequence[str] | None = (
    "0006_buyer_cart_sessions",
    "0007_buyers_unique_whatsapp",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
