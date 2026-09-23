from datetime import datetime
import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EarlyAccessLeadCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    business_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=5, max_length=50)
    email: str = Field(..., min_length=5, max_length=255)
    business_type: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    about_business: str = Field(..., min_length=5, max_length=2000)
    daily_whatsapp_orders: Optional[str] = Field(default=None, max_length=100)

    @field_validator("full_name", "business_name", "business_type", "city", "about_business")
    @classmethod
    def check_not_whitespace_only(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
            raise ValueError("Invalid email address format")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[^\d+]", "", v)
        if len(cleaned) < 8:
            raise ValueError("Phone number must contain at least 8 digits")
        return cleaned


class EarlyAccessLeadResponse(BaseModel):
    success: bool = True
    lead_id: str
    status: str
    message: str


class EarlyAccessLeadOut(BaseModel):
    id: str
    full_name: str
    business_name: str
    phone: str
    email: str
    business_type: str
    city: str
    about_business: str
    daily_whatsapp_orders: Optional[str] = None
    source: str
    status: str
    payment_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
