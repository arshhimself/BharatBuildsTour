"""Focused test suite for Ganesh Chaturthi Instagram demo post flow (Number A)."""

import pytest

from app.modules.runs.demo_ganesh import (
    GANESH_CHATURTHI_SUCCESS_RESPONSE,
    GANESH_CHATURTHI_TEMPLATE_RESPONSE,
    clear_owner_demo_state,
    get_ganesh_chaturthi_image_url,
    get_owner_demo_state,
    is_ganesh_chaturthi_insta_trigger,
)
from app.modules.runs.service import process_admin_message, process_buyer_message

pytest_plugins = ["test_phase1_postgres"]


@pytest.fixture(autouse=True)
def reset_demo_state():
    clear_owner_demo_state("919876543210")
    yield
    clear_owner_demo_state("919876543210")


def test_1_trigger_detection_positive():
    """1. Ganesh Chaturthi ke liye insta ka post banana -> demo handler triggers"""
    text = "Ganesh Chaturthi ke liye insta ka post banana"
    assert is_ganesh_chaturthi_insta_trigger(text) is True


def test_2_trigger_detection_missing_insta():
    """2. Message contains Ganesh Chaturthi but not insta -> demo handler does NOT trigger"""
    text = "Ganesh Chaturthi discount update for store"
    assert is_ganesh_chaturthi_insta_trigger(text) is False


def test_3_trigger_detection_missing_ganesh():
    """3. Message contains insta but not Ganesh Chaturthi -> demo handler does NOT trigger"""
    text = "Insta ka post banana for Diwali"
    assert is_ganesh_chaturthi_insta_trigger(text) is False


def test_4_trigger_returns_template_response():
    """4. Trigger -> template response returned"""
    outbound = process_admin_message(
        None, "919876543210", "Ganesh Chaturthi ke liye insta ka post banana"
    )
    assert len(outbound) == 2
    assert outbound[0].text == GANESH_CHATURTHI_TEMPLATE_RESPONSE


def test_5_trigger_includes_configured_image():
    """5. Trigger -> exact configured image is included as outbound WhatsApp image"""
    outbound = process_admin_message(
        None, "919876543210", "Ganesh Chaturthi ke liye insta ka post banana"
    )
    assert len(outbound) == 2
    assert outbound[1].message_type == "image"
    assert outbound[1].link == get_ganesh_chaturthi_image_url()


def test_6_trigger_persists_awaiting_approval_state():
    """6. Trigger -> awaiting_approval state persisted"""
    process_admin_message(None, "919876543210", "Ganesh Chaturthi ke liye insta ka post banana")
    state = get_owner_demo_state(None, "919876543210")
    assert state is not None
    assert state.get("pending_demo_action") == "ganesh_chaturthi_instagram_post"
    assert state.get("status") == "awaiting_approval"


def test_7_approval_returns_success_response():
    """7. Next message 'approved' -> 'Okay sir, this post is posted on your Instagram.'"""
    process_admin_message(None, "919876543210", "Ganesh Chaturthi ke liye insta ka post banana")
    outbound = process_admin_message(None, "919876543210", "approved")
    assert len(outbound) == 1
    assert outbound[0].text == GANESH_CHATURTHI_SUCCESS_RESPONSE


def test_8_approval_clears_pending_state():
    """8. Approval -> pending state cleared/completed"""
    process_admin_message(None, "919876543210", "Ganesh Chaturthi ke liye insta ka post banana")
    process_admin_message(None, "919876543210", "approved")
    state = get_owner_demo_state(None, "919876543210")
    assert state is not None
    assert state.get("pending_demo_action") is None
    assert state.get("status") == "completed"


def test_9_standalone_approved_without_pending_demo():
    """9. Standalone 'approved' without pending demo -> must NOT claim anything was posted"""
    outbound = process_admin_message(None, "919876543210", "approved")
    assert len(outbound) == 1
    assert GANESH_CHATURTHI_SUCCESS_RESPONSE not in outbound[0].text
    assert "posted on your Instagram" not in outbound[0].text


def test_10_number_b_unaffected(pg_session):
    """10. Number-B -> completely unaffected"""
    outbound = process_buyer_message(
        pg_session, "919876543210", "Ganesh Chaturthi ke liye insta ka post banana"
    )
    assert len(outbound) > 0
    assert outbound[0].text != GANESH_CHATURTHI_TEMPLATE_RESPONSE
    assert not any(
        getattr(m, "message_type", None) == "image" and m.link == get_ganesh_chaturthi_image_url()
        for m in outbound
    )
