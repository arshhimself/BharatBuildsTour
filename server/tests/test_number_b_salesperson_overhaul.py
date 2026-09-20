"""Regression coverage for production Number-B conversation and media failures."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.catalog.models import Product
from app.modules.commerce import customer_service, discovery_service
from app.modules.commerce.sales_tools import product_facts
from app.modules.identity.models import Business, Buyer
from app.modules.whatsapp.client import build_message_payload
from app.modules.whatsapp.models import WhatsAppMessage
from app.seed import DEMO_BUSINESS_ID
from seed_demo_clothing import seed_clothing_catalog

pytest_plugins = ["test_phase1_postgres"]


@pytest.fixture(autouse=True)
def no_external_llm(monkeypatch):
    monkeypatch.setattr(customer_service, "customer_salesperson_chat", lambda *_a, **_k: None)


def _persist_out(
    db: Session,
    *,
    phone: str,
    wa_id: str,
    context: dict,
    text: str = "options",
) -> None:
    db.add(
        WhatsAppMessage(
            provider_message_id=f"overhaul-{uuid4()}",
            direction="out",
            wa_id=wa_id,
            phone_number_id=phone,
            business_id=DEMO_BUSINESS_ID,
            payload={"text": text, "commerce_context": context},
            created_at=datetime.now(UTC),
        )
    )
    db.flush()


def _clothing_products(db: Session) -> dict[str, Product]:
    seed_clothing_catalog(db, DEMO_BUSINESS_ID)
    db.flush()
    names = {
        "Signature Black Zip Hoodie",
        "Navy Blue Linen Casual Shirt",
        "Navy Blue Two-Piece Tracksuit",
    }
    products = db.scalars(
        select(Product).where(
            Product.business_id == DEMO_BUSINESS_ID,
            Product.name.in_(names),
        )
    ).all()
    return {product.name: product for product in products}


def _state(ids: list[str], selected: str | None = None) -> dict:
    return {
        **customer_service._empty_state(),
        "shown_product_ids": ids,
        "selected_product_id": selected,
    }


def test_bata_na_browses_and_never_searches_for_na(pg_session: Session) -> None:
    _clothing_products(pg_session)
    responses = discovery_service.process_customer_commerce_message(
        pg_session,
        DEMO_BUSINESS_ID,
        "number-b-overhaul",
        "919100000001",
        "Bata na kya product hai",
    )
    context = responses[0].commerce_context
    assert context["tool_call"]["name"] == "browse_catalog"
    assert context["shown_product_ids"]
    assert context["tool_call"].get("arguments") != {"query": "na"}
    images = [message for message in responses if message.message_type == "image"]
    assert len(images) <= 3
    assert all(message.link and message.caption for message in images)


def test_semantic_reference_resolves_previously_shown_hoodie(pg_session: Session) -> None:
    products = _clothing_products(pg_session)
    hoodie = products["Signature Black Zip Hoodie"]
    ids = [str(product.id) for product in products.values()]
    _persist_out(
        pg_session,
        phone="number-b-semantic",
        wa_id="919100000002",
        context=_state(ids),
    )
    response = discovery_service.process_customer_commerce_message(
        pg_session,
        DEMO_BUSINESS_ID,
        "number-b-semantic",
        "919100000002",
        "I'm interested in Signature black zip hoodie",
    )
    assert response[0].commerce_context["selected_product_id"] == str(hoodie.id)
    assert hoodie.name in response[0].text
    assert "not found" not in response[0].text.casefold()
    assert any(message.message_type == "image" for message in response)


@pytest.mark.parametrize(
    ("phrase", "expected_index"),
    [("Bhai first waala product bata na", 0), ("second wala", 1)],
)
def test_ordinals_resolve_ordered_shown_products(
    pg_session: Session, phrase: str, expected_index: int
) -> None:
    products = _clothing_products(pg_session)
    ordered = [
        products["Signature Black Zip Hoodie"],
        products["Navy Blue Linen Casual Shirt"],
        products["Navy Blue Two-Piece Tracksuit"],
    ]
    ids = [str(product.id) for product in ordered]
    wa_id = f"9191{uuid4().int % 100000000:08d}"
    _persist_out(
        pg_session,
        phone="number-b-ordinal",
        wa_id=wa_id,
        context=_state(ids),
    )
    response = discovery_service.process_customer_commerce_message(
        pg_session,
        DEMO_BUSINESS_ID,
        "number-b-ordinal",
        wa_id,
        phrase,
    )[0]
    assert response.commerce_context["selected_product_id"] == ids[expected_index]
    assert ordered[expected_index].name in response.text
    assert "product naam ya category" not in response.text.casefold()


def test_selected_product_size_followups_use_real_variants(pg_session: Session) -> None:
    products = _clothing_products(pg_session)
    hoodie = products["Signature Black Zip Hoodie"]
    phone = "number-b-size"
    wa_id = "919100000003"
    state = _state([str(hoodie.id)], selected=str(hoodie.id))
    _persist_out(pg_session, phone=phone, wa_id=wa_id, context=state)

    sizes = discovery_service.process_customer_commerce_message(
        pg_session, DEMO_BUSINESS_ID, phone, wa_id, "iske sizes kya hai"
    )[0]
    assert all(size in sizes.text for size in ("S", "M", "L", "XL"))
    _persist_out(pg_session, phone=phone, wa_id=wa_id, context=sizes.commerce_context)

    medium = discovery_service.process_customer_commerce_message(
        pg_session, DEMO_BUSINESS_ID, phone, wa_id, "M hai?"
    )[0]
    assert "M available" in medium.text


def test_media_and_category_tools_are_tenant_scoped(pg_session: Session) -> None:
    products = _clothing_products(pg_session)
    hoodie = products["Signature Black Zip Hoodie"]
    facts = product_facts(pg_session, DEMO_BUSINESS_ID, [str(hoodie.id)])
    assert facts[0]["primary_media_url"].startswith("https://")

    other_business = Business(display_name=f"Isolated {uuid4()}")
    pg_session.add(other_business)
    pg_session.flush()
    assert product_facts(pg_session, other_business.id, [str(hoodie.id)]) == []


def test_actual_whatsapp_image_payload_uses_link_and_caption() -> None:
    payload = build_message_payload(
        to="919100000004",
        message_type="image",
        link="https://example.com/catalog/hoodie.jpg",
        caption="Signature Black Zip Hoodie\n₹2,799\nS / M / L / XL",
    )
    assert payload["type"] == "image"
    assert payload["image"] == {
        "link": "https://example.com/catalog/hoodie.jpg",
        "caption": "Signature Black Zip Hoodie\n₹2,799\nS / M / L / XL",
    }


def test_context_survives_independent_database_sessions(pg_engine, monkeypatch) -> None:
    monkeypatch.setattr(customer_service, "customer_salesperson_chat", lambda *_a, **_k: None)
    phone = "number-b-independent-session"
    wa_id = f"9192{uuid4().int % 100000000:08d}"
    with Session(pg_engine) as first:
        product_ids = [
            str(value)
            for value in first.scalars(
                select(Product.id)
                .where(Product.business_id == DEMO_BUSINESS_ID, Product.active.is_(True))
                .order_by(Product.sku)
                .limit(3)
            ).all()
        ]
        assert len(product_ids) == 3
        _persist_out(first, phone=phone, wa_id=wa_id, context=_state(product_ids))
        first.commit()

    with Session(pg_engine) as second:
        response = discovery_service.process_customer_commerce_message(
            second,
            DEMO_BUSINESS_ID,
            phone,
            wa_id,
            "first wala",
        )[0]
        assert response.commerce_context["selected_product_id"] == product_ids[0]
        second.rollback()


def test_fake_payment_claim_never_promotes_buyer(pg_session: Session) -> None:
    wa_id = "919100000005"
    response = discovery_service.process_customer_commerce_message(
        pg_session,
        DEMO_BUSINESS_ID,
        "number-b-payment",
        wa_id,
        "payment ho gaya bhai",
    )[0]
    assert "automatically update" in response.text
    buyer = pg_session.scalar(
        select(Buyer).where(
            Buyer.business_id == DEMO_BUSINESS_ID,
            Buyer.whatsapp_e164 == wa_id,
        )
    )
    assert buyer is not None and buyer.is_customer is False
