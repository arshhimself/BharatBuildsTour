"""Signed webhook Phase 1A + 1B acceptance on a disposable PostgreSQL database."""

import hashlib
import hmac
import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.main import app
from app.modules.identity.models import Business, Buyer
from app.modules.runs import service as runs_service
from app.modules.runs.conversation_graph import load_conversation_history
from app.modules.whatsapp import audio
from app.modules.whatsapp import client as whatsapp_client
from app.modules.whatsapp.models import WhatsAppMessage, WhatsAppNumberBinding
from app.seed import DEMO_BUSINESS_ID

pytest_plugins = ["test_phase1_postgres"]
_SECRET = "phase1-acceptance-only"  # pragma: allowlist secret
_SENDER = "919123456789"


def _signed(phone_id: str, message_id: str, text: str) -> tuple[bytes, dict[str, str]]:
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "waba-fixture",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "metadata": {"phone_number_id": phone_id},
                            "contacts": [
                                {"wa_id": _SENDER, "profile": {"name": "Synthetic Sender"}}
                            ],
                            "messages": [
                                {
                                    "from": _SENDER,
                                    "id": message_id,
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    digest = hmac.new(_SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return raw, {"X-Hub-Signature-256": f"sha256={digest}", "Content-Type": "application/json"}


def test_signed_webhook_commerce_a_to_g(pg_session: Session, monkeypatch) -> None:
    """The external signed route must preserve tenant, identity and experience."""
    other_business = uuid4()
    pg_session.add(Business(id=other_business, display_name="Other fixture merchant"))
    pg_session.add_all(
        [
            WhatsAppNumberBinding(
                phone_number_id="number-b",
                business_id=DEMO_BUSINESS_ID,
                experience="customer_commerce",
            ),
            WhatsAppNumberBinding(
                phone_number_id="number-b2",
                business_id=DEMO_BUSINESS_ID,
                experience="customer_commerce",
            ),
            WhatsAppNumberBinding(
                phone_number_id="number-a", business_id=DEMO_BUSINESS_ID, experience="owner_manager"
            ),
        ]
    )
    pg_session.flush()

    monkeypatch.setenv("WHATSAPP_APP_SECRET", _SECRET)
    monkeypatch.setenv("ADMIN_WHATSAPP_NUMBERS", _SENDER)
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-only-key")
    get_settings.cache_clear()

    sent: list[dict] = []
    owner_calls: list[str] = []

    async def no_read(*args, **kwargs):
        return None

    async def fake_send(**kwargs):
        sent.append(kwargs)
        return {"messages": [{"id": f"out-fixture-{len(sent)}"}]}

    def fake_owner(db, wa_id, text, phone_number_id=None):
        owner_calls.append(text)
        return [runs_service.OutboundMessage(to=wa_id, text="owner-only reply")]

    monkeypatch.setattr(whatsapp_client, "mark_read_with_typing", no_read)
    monkeypatch.setattr(whatsapp_client, "send_message", fake_send)
    monkeypatch.setattr(runs_service, "process_admin_message", fake_owner)
    monkeypatch.setattr(audio, "synthesize", lambda text: None)
    app.dependency_overrides[get_db] = lambda: pg_session

    try:
        with TestClient(app) as http:

            def post(phone: str, mid: str, text: str):
                raw, headers = _signed(phone, mid, text)
                return http.post("/webhook/whatsapp", content=raw, headers=headers)

            def commerce_contexts():
                messages = pg_session.scalars(
                    select(WhatsAppMessage).where(
                        WhatsAppMessage.direction == "out",
                        WhatsAppMessage.phone_number_id == "number-b",
                        WhatsAppMessage.business_id == DEMO_BUSINESS_ID,
                    )
                )
                return [
                    context
                    for message in messages
                    if isinstance(context := (message.payload or {}).get("commerce_context"), dict)
                ]

            def stamp_search(query: str, second: int):
                for message in pg_session.scalars(
                    select(WhatsAppMessage).where(WhatsAppMessage.direction == "out")
                ):
                    context = (message.payload or {}).get("commerce_context")
                    if isinstance(context, dict) and context.get("tool_call") == {
                        "name": "search_products",
                        "arguments": {"query": query},
                    }:
                        message.created_at = datetime(2026, 1, 1, 0, 0, second, tzinfo=UTC)
                pg_session.flush()

            # A: Number B creates one tenant-scoped lead and searches real catalog.
            assert post("number-b", "wamid.a", "LED chahiye").status_code == 200
            buyers = list(
                pg_session.scalars(
                    select(Buyer).where(
                        Buyer.business_id == DEMO_BUSINESS_ID, Buyer.whatsapp_e164 == _SENDER
                    )
                )
            )
            assert len(buyers) == 1 and buyers[0].is_customer is False
            assert {
                "name": "search_products",
                "arguments": {"query": "led"},
            } in [context["tool_call"] for context in commerce_contexts()]
            stamp_search("led", 1)

            # B: Follow-up reuses the Buyer and sees only this scoped conversation.
            assert post("number-b", "wamid.b", "12 watt wala").status_code == 200
            assert {
                "name": "search_products",
                "arguments": {"query": "12 watt"},
            } in [context["tool_call"] for context in commerce_contexts()]
            stamp_search("12 watt", 2)
            assert (
                len(
                    list(
                        pg_session.scalars(
                            select(Buyer).where(
                                Buyer.business_id == DEMO_BUSINESS_ID,
                                Buyer.whatsapp_e164 == _SENDER,
                            )
                        )
                    )
                )
                == 1
            )

            # C: Stock is read from the real tenant inventory tool.
            assert post("number-b", "wamid.c", "stock hai?").status_code == 200
            assert "check_inventory" in [
                context["tool_call"]["name"]
                for context in commerce_contexts()
                if context["tool_call"] is not None
            ]
            assert "available" in sent[2]["text"]

            # D: A payment claim is just text; no promotion.
            assert post("number-b", "wamid.d", "payment ho gaya").status_code == 200
            pg_session.refresh(buyers[0])
            assert buyers[0].is_customer is False

            # E: Number A goes to owner, not commerce, even for the same sender.
            commerce_before = len(sent)
            assert post("number-a", "wamid.e", "hello owner").status_code == 200
            assert owner_calls == ["hello owner"] and commerce_before == 4
            owner_history = load_conversation_history(
                pg_session, _SENDER, "number-a", business_id=DEMO_BUSINESS_ID
            )
            assert all("LED chahiye" not in turn["content"] for turn in owner_history)

            # F: Unknown receiving number fails closed.
            send_before = len(sent)
            assert post("unknown-number", "wamid.f", "hello").status_code == 403
            assert len(sent) == send_before

            # G: Meta replay cannot create another Buyer or execute commerce again.
            assert post("number-b", "wamid.a", "LED chahiye").status_code == 200
            assert len(sent) == send_before
            assert (
                len(
                    list(
                        pg_session.scalars(
                            select(Buyer).where(
                                Buyer.business_id == DEMO_BUSINESS_ID,
                                Buyer.whatsapp_e164 == _SENDER,
                            )
                        )
                    )
                )
                == 1
            )

            # Same sender / receiving number cannot see history after merchant remap.
            assert (
                load_conversation_history(
                    pg_session, _SENDER, "number-b", business_id=other_business
                )
                == []
            )
            assert (
                load_conversation_history(
                    pg_session, _SENDER, "number-b2", business_id=DEMO_BUSINESS_ID
                )
                == []
            )
            assert (
                len(
                    list(
                        pg_session.scalars(
                            select(WhatsAppMessage).where(
                                WhatsAppMessage.provider_message_id == "wamid.a"
                            )
                        )
                    )
                )
                == 1
            )
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
