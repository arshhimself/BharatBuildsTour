"""Demo-only Ganesh Chaturthi Instagram Post Flow for Owner/Manager Agent (Number A)."""

import logging
import os
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

GANESH_CHATURTHI_TEMPLATE_RESPONSE = (
    "Sir, Ganesh Chaturthi ke liye Instagram post ready kar diya hai. "
    "Please review karke approve kar dijiye."
)

GANESH_CHATURTHI_SUCCESS_RESPONSE = "Okay sir, this post is posted on your Instagram."

_IN_MEMORY_DEMO_STATES: dict[str, dict[str, Any]] = {}


def get_ganesh_chaturthi_image_url() -> str:
    override = os.environ.get("GANESH_CHATURTHI_DEMO_IMAGE_URL")
    if override:
        return override
    from app.api.routes.checkout import get_public_base_url

    return f"{get_public_base_url()}/api/demo/ganesh-chaturthi-image"


def is_ganesh_chaturthi_insta_trigger(text: str) -> bool:
    normalized = text.casefold()
    has_insta = "insta" in normalized or "instagram" in normalized
    has_ganesh = "ganesh" in normalized or "ganesha" in normalized
    has_chaturthi = "chaturthi" in normalized
    return has_insta and (has_ganesh and has_chaturthi)


def is_approval_message(text: str) -> bool:
    normalized = text.casefold().strip()
    exact_approvals = {
        "approved",
        "approve",
        "yes approved",
        "haan approved",
        "han approved",
        "post it",
        "ok approved",
        "okay approved",
    }
    if normalized in exact_approvals:
        return True
    words = set(normalized.split())
    if words and words <= {"approved", "approve", "yes", "haan", "han", "ok", "okay", "post", "it"}:
        if "approved" in words or "approve" in words or ("post" in words and "it" in words):
            return True
    return False


def get_owner_demo_state(db: Session | None, admin_wa_id: str) -> dict[str, Any] | None:
    if admin_wa_id in _IN_MEMORY_DEMO_STATES:
        return _IN_MEMORY_DEMO_STATES[admin_wa_id]

    if db is not None:
        try:
            from app.modules.whatsapp.models import WhatsAppMessage

            stmt = (
                select(WhatsAppMessage)
                .where(
                    WhatsAppMessage.wa_id == admin_wa_id,
                    WhatsAppMessage.direction == "out",
                )
                .order_by(WhatsAppMessage.created_at.desc())
                .limit(10)
            )
            rows = list(db.scalars(stmt).all())
            for msg in rows:
                p = msg.payload or {}
                if "pending_demo_action" in p:
                    state = {
                        "pending_demo_action": p.get("pending_demo_action"),
                        "status": p.get("status", ""),
                    }
                    _IN_MEMORY_DEMO_STATES[admin_wa_id] = state
                    return state
        except Exception as exc:
            logger.warning(f"Failed to fetch demo state from DB: {exc}")

    return None


def set_owner_demo_state(
    db: Session | None,
    admin_wa_id: str,
    pending_demo_action: str | None,
    status: str,
) -> None:
    state_data = {
        "pending_demo_action": pending_demo_action,
        "status": status,
    }
    _IN_MEMORY_DEMO_STATES[admin_wa_id] = state_data

    if db is not None:
        try:
            from app.modules.whatsapp.models import WhatsAppMessage

            stmt = (
                select(WhatsAppMessage)
                .where(
                    WhatsAppMessage.wa_id == admin_wa_id,
                    WhatsAppMessage.direction == "out",
                )
                .order_by(WhatsAppMessage.created_at.desc())
                .limit(1)
            )
            msg = db.scalar(stmt)
            if msg:
                payload = dict(msg.payload or {})
                payload.update(state_data)
                msg.payload = payload
                db.flush()
        except Exception as exc:
            logger.warning(f"Failed to persist demo state to DB: {exc}")


def clear_owner_demo_state(admin_wa_id: str) -> None:
    _IN_MEMORY_DEMO_STATES.pop(admin_wa_id, None)


def handle_owner_demo_flow(
    db: Session | None,
    admin_wa_id: str,
    text_body: str,
) -> list[Any] | None:
    from app.modules.runs.service import OutboundMessage

    state = get_owner_demo_state(db, admin_wa_id)

    # 1. Check if owner is approving a pending demo post
    if (
        state
        and state.get("pending_demo_action") == "ganesh_chaturthi_instagram_post"
        and state.get("status") == "awaiting_approval"
    ):
        if is_approval_message(text_body):
            demo_state = {
                "pending_demo_action": None,
                "status": "completed",
            }
            set_owner_demo_state(
                db,
                admin_wa_id,
                pending_demo_action=None,
                status="completed",
            )
            return [
                OutboundMessage(
                    to=admin_wa_id,
                    text=GANESH_CHATURTHI_SUCCESS_RESPONSE,
                    demo_state=demo_state,
                )
            ]

    # 2. Check if owner is triggering the demo post flow
    if is_ganesh_chaturthi_insta_trigger(text_body):
        demo_state = {
            "pending_demo_action": "ganesh_chaturthi_instagram_post",
            "status": "awaiting_approval",
        }
        set_owner_demo_state(
            db,
            admin_wa_id,
            pending_demo_action="ganesh_chaturthi_instagram_post",
            status="awaiting_approval",
        )
        return [
            OutboundMessage(
                to=admin_wa_id,
                text=GANESH_CHATURTHI_TEMPLATE_RESPONSE,
                demo_state=demo_state,
            ),
            OutboundMessage(
                to=admin_wa_id,
                message_type="image",
                link=get_ganesh_chaturthi_image_url(),
                demo_state=demo_state,
            ),
        ]

    return None
