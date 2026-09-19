"""Add social_posts table for Social Media Agent & Instagram Publishing.

Revision ID: 0009_social_posts
Revises: e5b4a228093f
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009_social_posts"
down_revision: str | Sequence[str] | None = "e5b4a228093f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "social_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("platform", sa.String(length=32), nullable=False, server_default="instagram"),
        sa.Column("platform_account_id", sa.String(length=128), nullable=True),
        sa.Column("media_id", sa.String(length=128), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PUBLISHED"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("social_posts")
