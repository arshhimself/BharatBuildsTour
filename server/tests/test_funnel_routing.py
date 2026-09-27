from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from app.modules.catalog.models import Product, ProductVariant
from app.modules.commerce import customer_service
from app.modules.commerce.customer_service import (
    load_commerce_state,
    process_customer_commerce_message,
)
from app.modules.whatsapp.models import WhatsAppMessage

pytest_plugins = ["test_phase1_postgres"]


@pytest.fixture(autouse=True)
def no_external_llm(monkeypatch):
    from app.modules.commerce.salesperson import SalespersonTurn

    def mock_chat(
        db, business_id, buyer_id, phone_number_id, wa_id, message, previous=None, **kwargs
    ):
        print(f"DEBUG MOCK: message={message}, previous={previous}")
        updates = {}
        if "address" in message.lower() or "chembur" in message.lower():
            updates["shipping_address"] = "Chembur"
        return SalespersonTurn(
            text="Mocked", tool_call=None, state_updates=updates, outbound_media=[]
        )

    monkeypatch.setattr(customer_service, "customer_salesperson_chat", mock_chat)


@pytest.fixture
def store_setup(pg_session: Session):
    from app.modules.identity.models import Business
    from app.seed import DEMO_BUSINESS_ID
    from seed_demo_clothing import seed_clothing_catalog

    business = pg_session.query(Business).filter(Business.id == DEMO_BUSINESS_ID).first()
    if not pg_session.query(Product).filter(Product.sku == "CLOTH-TSHIRT-BLK").first():
        seed_clothing_catalog(pg_session, business.id)
    return business


def _simulate_webhook_reply(
    pg_session: Session, business_id: UUID, wa_id: str, text: str, replied_to_message_id: str
):
    # This simulates `app/modules/whatsapp/service.py` extracting `context.id`
    import uuid

    inbound_id = f"wamid.{uuid.uuid4()}"
    msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        created_at=datetime.now(UTC),
        direction="in",
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=business_id,
        payload={"replied_to_message_id": replied_to_message_id},
    )
    pg_session.add(msg)
    pg_session.commit()
    return process_customer_commerce_message(
        pg_session, business_id, "12345", wa_id, text, inbound_message_id=inbound_id
    )


def test_a_native_reply_selects_product(pg_session: Session, store_setup):
    wa_id = "919999999991"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )

    # Simulate prior outbound message with commerce_context
    outbound_id = "wamid.outbound_1"
    msg = WhatsAppMessage(
        provider_message_id=outbound_id,
        direction="out",
        created_at=datetime.now(UTC) - timedelta(seconds=10),
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"commerce_context": {"version": 2, "selected_product_id": str(product.id)}},
    )
    pg_session.add(msg)
    pg_session.commit()

    import uuid

    inbound_id = f"wamid.{uuid.uuid4()}"
    inbound_msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        created_at=datetime.now(UTC),
        direction="in",
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"replied_to_message_id": outbound_id},
    )
    pg_session.add(inbound_msg)
    pg_session.commit()

    # Act
    process_customer_commerce_message(
        pg_session,
        store_setup.id,
        "12345",
        wa_id,
        "Mujhe ye chahiye",
        inbound_message_id=inbound_id,
    )

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)

    assert state["selected_product_id"] == str(product.id)
    assert state.get("last_search_query") != "ye"


def test_c_l_while_awaiting_variant(pg_session: Session, store_setup):
    wa_id = "919999999997"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )

    outbound_id = "wamid.outbound_c"
    msg = WhatsAppMessage(
        provider_message_id=outbound_id,
        direction="out",
        created_at=datetime.now(UTC) - timedelta(seconds=10),
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"commerce_context": {"version": 2, "selected_product_id": str(product.id)}},
    )
    pg_session.add(msg)
    pg_session.commit()
    import uuid

    inbound_id = f"wamid.{uuid.uuid4()}"
    inbound_msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        created_at=datetime.now(UTC),
        direction="in",
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={},
    )
    pg_session.add(inbound_msg)
    pg_session.commit()

    process_customer_commerce_message(
        pg_session, store_setup.id, "12345", wa_id, "L", inbound_message_id=inbound_id
    )
    pg_session.commit()

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)

    assert state["selected_size"] == "L"


def test_d_ek_hi_chahiye_sets_quantity(pg_session: Session, store_setup):
    wa_id = "919999999992"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )

    # Manually inject previous state
    outbound_id = "wamid.outbound_2"
    msg = WhatsAppMessage(
        provider_message_id=outbound_id,
        direction="out",
        created_at=datetime.now(UTC) - timedelta(seconds=10),
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"commerce_context": {"version": 2, "selected_product_id": str(product.id)}},
    )
    pg_session.add(msg)
    pg_session.commit()

    process_customer_commerce_message(pg_session, store_setup.id, "12345", wa_id, "Ek hi chahiye")

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)
    print("TEST D LOADED STATE:", state)

    assert state["quantity"] == 1
    tool_call = state.get("tool_call") or {}
    assert "catalog mein" not in tool_call.get("name", "")


def test_e_1_while_quantity_missing(pg_session: Session, store_setup):
    wa_id = "919999999998"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )

    outbound_id = "wamid.outbound_e"
    msg = WhatsAppMessage(
        provider_message_id=outbound_id,
        direction="out",
        created_at=datetime.now(UTC) - timedelta(seconds=10),
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"commerce_context": {"version": 2, "selected_product_id": str(product.id)}},
    )
    pg_session.add(msg)
    pg_session.commit()

    process_customer_commerce_message(pg_session, store_setup.id, "12345", wa_id, "1")

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)

    assert state["quantity"] == 1
    tool_call = state.get("tool_call") or {}
    assert "catalog mein" not in tool_call.get("name", "")


def test_f_size_and_quantity_in_same_turn(pg_session: Session, store_setup):
    wa_id = "919999999993"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )

    outbound_id = "wamid.outbound_3"
    msg = WhatsAppMessage(
        provider_message_id=outbound_id,
        direction="out",
        created_at=datetime.now(UTC) - timedelta(seconds=10),
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"commerce_context": {"version": 2, "selected_product_id": str(product.id)}},
    )
    pg_session.add(msg)
    pg_session.commit()

    import uuid

    inbound_id = f"wamid.{uuid.uuid4()}"
    inbound_msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        created_at=datetime.now(UTC),
        direction="in",
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"replied_to_message_id": outbound_id},
    )
    pg_session.add(inbound_msg)
    pg_session.commit()

    process_customer_commerce_message(
        pg_session,
        store_setup.id,
        "12345",
        wa_id,
        "L size, ek hi chahiye",
        inbound_message_id=inbound_id,
    )
    pg_session.commit()

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)

    assert state["selected_size"] == "L"
    assert state["quantity"] == 1


def test_h_multi_slot_extraction(pg_session: Session, store_setup):
    wa_id = "919999999994"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )

    outbound_id = "wamid.outbound_4"
    msg = WhatsAppMessage(
        provider_message_id=outbound_id,
        direction="out",
        created_at=datetime.now(UTC) - timedelta(seconds=10),
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"commerce_context": {"version": 2, "selected_product_id": str(product.id)}},
    )
    pg_session.add(msg)
    pg_session.commit()

    import uuid

    inbound_id = f"wamid.{uuid.uuid4()}"
    inbound_msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        created_at=datetime.now(UTC),
        direction="in",
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"replied_to_message_id": outbound_id},
    )
    pg_session.add(inbound_msg)
    pg_session.commit()

    process_customer_commerce_message(
        pg_session,
        store_setup.id,
        "12345",
        wa_id,
        "Ye hi chahiye L size me, address Chembur hai aur ek hi chahiye",
        inbound_message_id=inbound_id,
    )
    pg_session.commit()

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)
    assert state["selected_size"] == "L"
    assert state["quantity"] == 1
    assert state.get("shipping_address") == "Chembur"


def test_j_native_reply_ye_wala_2_quantity(pg_session: Session, store_setup):
    wa_id = "919999999999"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )

    outbound_id = "wamid.outbound_j"
    msg = WhatsAppMessage(
        provider_message_id=outbound_id,
        direction="out",
        created_at=datetime.now(UTC) - timedelta(seconds=10),
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"commerce_context": {"selected_product_id": str(product.id)}},
    )
    pg_session.add(msg)
    pg_session.commit()

    import uuid

    inbound_id = f"wamid.{uuid.uuid4()}"
    inbound_msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        created_at=datetime.now(UTC),
        direction="in",
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"replied_to_message_id": outbound_id},
    )
    pg_session.add(inbound_msg)
    pg_session.commit()

    process_customer_commerce_message(
        pg_session,
        store_setup.id,
        "12345",
        wa_id,
        "Ye wala 2 quantity",
        inbound_message_id=inbound_id,
    )

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)

    assert state["selected_product_id"] == str(product.id)
    assert state["quantity"] == 2


def test_k_xl_ke_2_piece(pg_session: Session, store_setup):
    wa_id = "919999999995"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )

    outbound_id = "wamid.outbound_5"
    msg = WhatsAppMessage(
        provider_message_id=outbound_id,
        direction="out",
        created_at=datetime.now(UTC) - timedelta(seconds=10),
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"commerce_context": {"selected_product_id": str(product.id)}},
    )
    pg_session.add(msg)
    pg_session.commit()

    import uuid

    inbound_id = f"wamid.{uuid.uuid4()}"
    inbound_msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        created_at=datetime.now(UTC),
        direction="in",
        wa_id=wa_id,
        phone_number_id="12345",
        business_id=store_setup.id,
        payload={"replied_to_message_id": outbound_id},
    )
    pg_session.add(inbound_msg)
    pg_session.commit()

    process_customer_commerce_message(
        pg_session, store_setup.id, "12345", wa_id, "XL ke 2 piece", inbound_message_id=inbound_id
    )

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)

    assert state["selected_size"] == "XL"
    assert state["quantity"] == 2


def test_l_arey_wo_product_chahiye_no_fallback(pg_session: Session, store_setup):
    wa_id = "919999999996"
    product = (
        pg_session.query(Product)
        .join(ProductVariant)
        .filter(ProductVariant.size.ilike("L"))
        .first()
    )
    process_customer_commerce_message(
        pg_session, store_setup.id, "12345", wa_id, f"I want {product.name}"
    )
    out = process_customer_commerce_message(
        pg_session, store_setup.id, "12345", wa_id, "Arey wo product chahiye"
    )

    assert "catalog mein" not in out[0].text
    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)

    assert state.get("last_search_query") not in ("arey wo", "arey")


def test_m_ambiguous_wo_wala(pg_session: Session, store_setup):
    wa_id = "919999999990"
    process_customer_commerce_message(pg_session, store_setup.id, "12345", wa_id, "wo wala")

    state = load_commerce_state(pg_session, store_setup.id, "12345", wa_id)

    assert state.get("last_search_query") != "wo wala"
    assert "catalog mein" not in str(state.get("tool_call", {}))
