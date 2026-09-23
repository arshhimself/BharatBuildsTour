"""early_access_leads table

Revision ID: 0009_early_access_leads
Revises: 5611c80ac78c
Create Date: 2026-09-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0009_early_access_leads'
down_revision: Union[str, None] = '5611c80ac78c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'early_access_leads',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('business_type', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('about_business', sa.Text(), nullable=False),
        sa.Column('daily_whatsapp_orders', sa.String(length=100), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False, server_default='website_early_access'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='new'),
        sa.Column('payment_status', sa.String(length=50), nullable=False, server_default='not_started'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_early_access_leads_phone', 'early_access_leads', ['phone'], unique=False)
    op.create_index('ix_early_access_leads_email', 'early_access_leads', ['email'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_early_access_leads_email', table_name='early_access_leads')
    op.drop_index('ix_early_access_leads_phone', table_name='early_access_leads')
    op.drop_table('early_access_leads')
