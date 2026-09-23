from datetime import datetime, timezone, timedelta
from typing import Tuple, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.early_access.models import EarlyAccessLead
from app.modules.early_access.schemas import EarlyAccessLeadCreate


def create_or_get_early_access_lead(
    db: Session, data: EarlyAccessLeadCreate
) -> Tuple[EarlyAccessLead, bool]:
    """Saves lead to database.
    Checks for duplicate submission (same phone or email within last 1 hour).
    Returns (lead, is_new).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

    # Check for recent duplicate
    stmt = (
        select(EarlyAccessLead)
        .where(
            (EarlyAccessLead.phone == data.phone) | (EarlyAccessLead.email == data.email)
        )
        .where(EarlyAccessLead.created_at >= cutoff)
        .order_by(EarlyAccessLead.created_at.desc())
    )
    existing = db.execute(stmt).scalars().first()
    if existing:
        return existing, False

    lead = EarlyAccessLead(
        full_name=data.full_name,
        business_name=data.business_name,
        phone=data.phone,
        email=data.email,
        business_type=data.business_type,
        city=data.city,
        about_business=data.about_business,
        daily_whatsapp_orders=data.daily_whatsapp_orders,
        source="website_early_access",
        status="new",
        payment_status="not_started",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead, True


def get_all_early_access_leads(db: Session, limit: int = 100) -> List[EarlyAccessLead]:
    stmt = select(EarlyAccessLead).order_by(EarlyAccessLead.created_at.desc()).limit(limit)
    return list(db.execute(stmt).scalars().all())
