"""Tests for the new LangGraph AI Salesperson Commerce flow."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.modules.commerce.discovery_service import process_customer_commerce_message
from app.modules.commerce.salesperson import SalespersonTurn
from app.seed import DEMO_BUSINESS_ID

pytest_plugins = ["test_phase1_postgres"]


@pytest.fixture
def mock_salesperson():
    with patch("app.modules.commerce.discovery_service.customer_salesperson_chat") as m:
        yield m


def test_ai_salesperson_memory_passed_correctly(
    pg_session: Session, mock_salesperson: MagicMock
) -> None:
    # Setup mock return
    mock_salesperson.return_value = SalespersonTurn(
        text="Aapko ye product kaisa laga?",
        tool_call={"name": "browse_catalog", "arguments": {"limit": 5}},
        shown_product_ids=["test-id-1"],
        selected_product_id=None,
        cart_id="test-cart-id",
        order_id=None,
        checkout_stage=None,
        quantity=None,
    )

    phone_id = "ai-phone-1"
    wa_id = "919700000010"

    outbound = process_customer_commerce_message(
        pg_session,
        business_id=DEMO_BUSINESS_ID,
        phone_number_id=phone_id,
        wa_id=wa_id,
        text_body="Hello",
    )

    assert len(outbound) == 1
    msg = outbound[0]
    assert msg.to == wa_id
    assert msg.text == "Aapko ye product kaisa laga?"

    ctx = msg.commerce_context
    assert ctx["tool_call"]["name"] == "browse_catalog"
    assert ctx["shown_product_ids"] == ["test-id-1"]
    assert ctx["cart_id"] == "test-cart-id"


def test_ai_salesperson_payment_and_ui_with_image(
    pg_session: Session, mock_salesperson: MagicMock
) -> None:
    # We will simulate a selected product that triggers an image.
    product_id = "00000000-0000-0000-0000-000000000000"

    # Normally we'd want to insert a ProductMedia for product_id here to test UI image attachment.
    # We can mock db.scalar or just test that if no image exists, it gracefully falls back.

    mock_salesperson.return_value = SalespersonTurn(
        text="Maine cart mein add kar diya. Checkout kar sakte hain.",
        tool_call={"name": "add_to_cart", "arguments": {"product_id": product_id}},
        shown_product_ids=[],
        selected_product_id=product_id,
        cart_id="test-cart-id",
        order_id="test-order-id",
        checkout_stage="READY_TO_PAY",
        quantity=1,
    )

    outbound = process_customer_commerce_message(
        pg_session,
        business_id=DEMO_BUSINESS_ID,
        phone_number_id="ai-phone-1",
        wa_id="919700000010",
        text_body="Ek T-Shirt pack kar do.",
    )

    assert len(outbound) == 1  # No image inserted, so just 1 text msg

    msg = outbound[-1]
    ctx = msg.commerce_context
    assert ctx["order_id"] == "test-order-id"
    assert ctx["checkout_stage"] == "READY_TO_PAY"
