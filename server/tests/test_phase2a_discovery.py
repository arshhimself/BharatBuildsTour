"""Phase 2A deterministic WhatsApp commerce discovery regression coverage."""

import inspect
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.modules.catalog.service import get_product
from app.modules.commerce import discovery_service
from app.modules.commerce.discovery import DiscoveryKind, interpret_discovery_message
from app.modules.identity.models import Business, Buyer
from app.modules.whatsapp.models import WhatsAppMessage
from app.seed import DEMO_BUSINESS_ID

pytest_plugins = ["test_phase1_postgres"]


@pytest.mark.parametrize(
    "text",
    [
        "Aapke products jaanna hai mujhe",
        "kya kya bechte ho?",
        "what do you sell?",
        "what products do you have?",
        "products dikhao",
        "catalogue batao",
        "kuch options dikhao",
        "आपके प्रोडक्ट्स बताओ",
    ],
)
def test_broad_discovery_routes_to_browse(text: str) -> None:
    request = interpret_discovery_message(text)
    assert request.kind is DiscoveryKind.BROWSE
    assert request.query is None


@pytest.mark.parametrize(
    ("text", "query"),
    [
        ("LED dikhao", "led"),
        ("wire chahiye", "wire"),
        ("12 watt light hai?", "12 watt led"),
        ("MCB available hai?", "mcb"),
        ("XYZABC product hai?", "xyzabc"),
    ],
)
def test_specific_search_has_clean_current_turn_query(text: str, query: str) -> None:
    request = interpret_discovery_message(text)
    assert request.kind is DiscoveryKind.SEARCH
    assert request.query == query
    assert request.query in {"led", "wire", "12 watt led", "mcb", "xyzabc"}


@pytest.mark.parametrize(
    ("text", "minimum", "maximum"),
    [
        ("1500 ke andar kya hai?", None, 150_000),
        ("1000 se 2000 ke beech kuch dikhao", 100_000, 200_000),
        ("sasta option hai?", None, None),
        ("cheaper wala?", None, None),
    ],
)
def test_price_language_is_not_product_search(
    text: str, minimum: int | None, maximum: int | None
) -> None:
    request = interpret_discovery_message(text)
    assert request.kind is DiscoveryKind.PRICE_FILTER
    assert request.min_price_paise == minimum
    assert request.max_price_paise == maximum


def _persist_response(
    session: Session,
    *,
    business_id,
    phone_number_id: str,
    wa_id: str,
    sequence: int,
    message,
) -> None:
    session.add(
        WhatsAppMessage(
            provider_message_id=f"phase2a-out-{wa_id}-{sequence}",
            direction="out",
            wa_id=wa_id,
            phone_number_id=phone_number_id,
            business_id=business_id,
            created_at=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=sequence),
            payload={
                "text": message.text,
                "commerce_context": message.commerce_context,
            },
        )
    )
    session.flush()


def _turn(
    session: Session,
    *,
    business_id=DEMO_BUSINESS_ID,
    phone_number_id: str,
    wa_id: str,
    sequence: int,
    text: str,
):
    response = discovery_service.process_customer_commerce_message(
        session,
        business_id,
        phone_number_id,
        wa_id,
        text,
    )[0]
    _persist_response(
        session,
        business_id=business_id,
        phone_number_id=phone_number_id,
        wa_id=wa_id,
        sequence=sequence,
        message=response,
    )
    return response


def test_manual_like_discovery_reference_inventory_and_unknown(pg_session: Session) -> None:
    phone_id = "phase2a-number-b"
    wa_id = "919700000001"

    hello = _turn(
        pg_session,
        phone_number_id=phone_id,
        wa_id=wa_id,
        sequence=1,
        text="Hello",
    )
    assert hello.commerce_context["route"] == "chat"

    browse = _turn(
        pg_session,
        phone_number_id=phone_id,
        wa_id=wa_id,
        sequence=2,
        text="Aapke products jaanna hai mujhe",
    )
    browse_context = browse.commerce_context
    assert browse_context["tool_call"] == {"name": "browse_catalog", "arguments": {"limit": 5}}
    assert browse_context["shown_product_ids"]
    assert "Aapke products jaanna hai mujhe" not in str(browse_context["tool_call"])

    led = _turn(
        pg_session,
        phone_number_id=phone_id,
        wa_id=wa_id,
        sequence=3,
        text="LED dikhao",
    )
    led_context = led.commerce_context
    assert led_context["tool_call"]["name"] == "search_products"
    assert led_context["tool_call"]["arguments"] == {"query": "led"}
    assert len(led_context["shown_product_ids"]) >= 2

    second = _turn(
        pg_session,
        phone_number_id=phone_id,
        wa_id=wa_id,
        sequence=4,
        text="second wala",
    )
    selected_id = second.commerce_context["selected_product_id"]
    assert selected_id == led_context["shown_product_ids"][1]
    assert second.commerce_context["tool_call"] == {
        "name": "get_product",
        "arguments": {"product_id": selected_id},
    }

    stock = _turn(
        pg_session,
        phone_number_id=phone_id,
        wa_id=wa_id,
        sequence=5,
        text="iska stock hai?",
    )
    assert stock.commerce_context["tool_call"] == {
        "name": "check_inventory",
        "arguments": {"product_id": selected_id, "requested_qty": 1},
    }
    assert "available" in stock.text

    budget = _turn(
        pg_session,
        phone_number_id=phone_id,
        wa_id=wa_id,
        sequence=6,
        text="1500 ke andar kya hai?",
    )
    assert budget.commerce_context["tool_call"] == {
        "name": "filter_products_by_price",
        "arguments": {
            "min_price_paise": None,
            "max_price_paise": 150_000,
            "limit": 5,
        },
    }
    for product_id in budget.commerce_context["shown_product_ids"]:
        product = get_product(pg_session, DEMO_BUSINESS_ID, UUID(product_id))
        assert product is not None
        assert product.base_unit_price_paise <= 150_000

    unknown = _turn(
        pg_session,
        phone_number_id=phone_id,
        wa_id=wa_id,
        sequence=7,
        text="XYZABC hai?",
    )
    assert unknown.commerce_context["tool_call"]["arguments"] == {"query": "xyzabc"}
    assert unknown.commerce_context["shown_product_ids"] == []
    assert "nahi mila" in unknown.text

    buyer = pg_session.scalar(
        select(Buyer).where(
            Buyer.business_id == DEMO_BUSINESS_ID,
            Buyer.whatsapp_e164 == wa_id,
        )
    )
    assert buyer is not None and buyer.is_customer is False
    payment_claim = _turn(
        pg_session,
        phone_number_id=phone_id,
        wa_id=wa_id,
        sequence=8,
        text="payment ho gaya",
    )
    assert payment_claim.commerce_context["route"] == "chat"
    pg_session.refresh(buyer)
    assert buyer.is_customer is False


def test_alias_facts_and_tenant_isolation(pg_session: Session) -> None:
    alias = _turn(
        pg_session,
        phone_number_id="phase2a-number-b",
        wa_id="919700000002",
        sequence=1,
        text="cable chahiye",
    )
    assert alias.commerce_context["tool_call"]["arguments"] == {"query": "cable"}
    assert alias.commerce_context["shown_product_ids"]
    first_id = alias.commerce_context["shown_product_ids"][0]
    product = get_product(pg_session, DEMO_BUSINESS_ID, UUID(first_id))
    assert product is not None
    assert product.name in alias.text
    assert product.sku in alias.text
    assert f"₹{product.base_unit_price_paise / 100:,.2f}" in alias.text

    other_business_id = uuid4()
    pg_session.execute(
        insert(Business).values(id=other_business_id, display_name="Phase 2A isolated merchant")
    )
    isolated = _turn(
        pg_session,
        business_id=other_business_id,
        phone_number_id="phase2a-number-other",
        wa_id="919700000003",
        sequence=1,
        text="products dikhao",
    )
    assert isolated.commerce_context["shown_product_ids"] == []
    assert "available nahi" in isolated.text


def test_reference_state_is_business_phone_and_sender_scoped(pg_session: Session) -> None:
    shown = _turn(
        pg_session,
        phone_number_id="phase2a-number-one",
        wa_id="919700000004",
        sequence=1,
        text="LED dikhao",
    )
    assert shown.commerce_context["shown_product_ids"]

    other_number = discovery_service.process_customer_commerce_message(
        pg_session,
        DEMO_BUSINESS_ID,
        "phase2a-number-two",
        "919700000004",
        "second wala",
    )[0]
    assert other_number.commerce_context["selected_product_id"] is None

    other_sender = discovery_service.process_customer_commerce_message(
        pg_session,
        DEMO_BUSINESS_ID,
        "phase2a-number-one",
        "919700000005",
        "second wala",
    )[0]
    assert other_sender.commerce_context["selected_product_id"] is None


def test_customer_commerce_path_has_no_mock_desks_dependency() -> None:
    source = inspect.getsource(discovery_service)
    assert "mock_desks" not in source
