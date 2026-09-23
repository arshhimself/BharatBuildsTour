from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.early_access.schemas import (
    EarlyAccessLeadCreate,
    EarlyAccessLeadResponse,
    EarlyAccessLeadOut,
)
from app.modules.early_access.service import (
    create_or_get_early_access_lead,
    get_all_early_access_leads,
)

from app.api.owner_auth import CurrentUser

router = APIRouter(prefix="/early-access", tags=["early-access"])


@router.post("/leads", response_model=EarlyAccessLeadResponse, status_code=status.HTTP_201_CREATED)
def submit_early_access_lead(
    payload: EarlyAccessLeadCreate,
    db: Session = Depends(get_db),
):
    try:
        lead, is_new = create_or_get_early_access_lead(db, payload)
        if not is_new:
            return EarlyAccessLeadResponse(
                success=True,
                lead_id=lead.id,
                status=lead.status,
                message="We already have your request. Our team will contact you shortly.",
            )
        return EarlyAccessLeadResponse(
            success=True,
            lead_id=lead.id,
            status=lead.status,
            message="Request received successfully.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while saving your request. Please try again.",
        )


@router.get("/leads", response_model=List[EarlyAccessLeadOut])
def list_early_access_leads(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return get_all_early_access_leads(db)
