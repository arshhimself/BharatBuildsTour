"""Production Number-B orchestration: references, persistence, LLM, and media."""

import hashlib
import logging
import re
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.catalog.models import ProductAlias
from app.modules.catalog.normalization import normalize_catalog_text
from app.modules.commerce.discovery import DiscoveryKind, interpret_discovery_message
from app.modules.commerce.sales_tools import product_facts
from app.modules.commerce.salesperson import clean_whatsapp_text, customer_salesperson_chat
from app.modules.identity.service import resolve_or_create_whatsapp_buyer
from app.modules.runs.service import OutboundMessage
from app.modules.whatsapp.models import WhatsAppMessage

logger = logging.getLogger(__name__)

CONTEXT_VERSION = 2
MEDIA_LIMIT = 3
_REFERENCE_NOISE = {
    "a",
    "acha",
    "bhai",
    "hai",
    "i",
    "im",
    "in",
    "interested",
    "is",
    "ka",
    "ki",
    "ko",
    "me",
    "mein",
    "mujhe",
    "na",
    "product",
    "the",
    "this",
    "wala",
    "waala",
    "wo",
    "woh",
    "ye",
}


def _empty_state() -> dict[str, Any]:
    return {
        "version": CONTEXT_VERSION,
        "route": None,
        "last_intent": None,
        "last_search_query": None,
        "last_category_id": None,
        "shown_product_ids": [],
        "shown_variant_ids": [],
        "selected_product_id": None,
        "selected_variant_id": None,
        "selected_size": None,
        "selected_color": None,
        "quantity": 1,
        "cart_id": None,
        "order_id": None,
        "checkout_session_id": None,
        "checkout_stage": None,
        "last_recommendation_reason": None,
        "tool_call": None,
    }


def load_commerce_state(
    db: Session, business_id: UUID, phone_number_id: str, wa_id: str
) -> dict[str, Any]:
    rows = db.scalars(
        select(WhatsAppMessage)
        .where(
            WhatsAppMessage.business_id == business_id,
            WhatsAppMessage.phone_number_id == phone_number_id,
            WhatsAppMessage.wa_id == wa_id,
        )
        .order_by(WhatsAppMessage.created_at.desc(), WhatsAppMessage.id.desc())
        .limit(20)
    )
    state = _empty_state()
    for row in rows:
        context = (row.payload or {}).get("commerce_context")
        if not isinstance(context, dict):
            continue
        if context.get("version") not in {1, CONTEXT_VERSION}:
            continue
        state.update({key: value for key, value in context.items() if key in state})
        state["version"] = CONTEXT_VERSION
        return state
    return state


def _persist_on_inbound(
    db: Session,
    business_id: UUID,
    phone_number_id: str,
    wa_id: str,
    inbound_message_id: str | None,
    state: dict[str, Any],
) -> None:
    if not inbound_message_id:
        return
    row = db.scalar(
        select(WhatsAppMessage).where(
            WhatsAppMessage.provider_message_id == inbound_message_id,
            WhatsAppMessage.direction == "in",
            WhatsAppMessage.business_id == business_id,
            WhatsAppMessage.phone_number_id == phone_number_id,
            WhatsAppMessage.wa_id == wa_id,
        )
    )
    if row is None:
        return
    row.payload = {**(row.payload or {}), "commerce_context": state}
    db.flush()


def _attach(message: OutboundMessage, state: dict[str, Any]) -> OutboundMessage:
    message.commerce_context = state
    return message


def _price(paise: int) -> str:
    amount = paise / 100
    return f"₹{amount:,.0f}" if paise % 100 == 0 else f"₹{amount:,.2f}"


def _caption(product: dict[str, Any]) -> str:
    lines = [product["name"], _price(product["price_paise"])]
    sizes = [variant.get("size") for variant in product.get("variants", []) if variant.get("size")]
    colors = [
        variant.get("color") for variant in product.get("variants", []) if variant.get("color")
    ]
    detail = []
    if colors:
        detail.append(" / ".join(dict.fromkeys(colors)))
    if sizes:
        detail.append(" / ".join(dict.fromkeys(sizes)))
    if detail:
        lines.append(" • ".join(detail))
    return "\n".join(lines)


def _messages(
    wa_id: str,
    text: str,
    state: dict[str, Any],
    db: Session,
    business_id: UUID,
    media: list[dict[str, str]] | None = None,
) -> list[OutboundMessage]:
    outbound = [_attach(OutboundMessage(to=wa_id, text=clean_whatsapp_text(text)), state)]
    media = media or []
    facts = {
        product["id"]: product
        for product in product_facts(
            db,
            business_id,
            [item["product_id"] for item in media if item.get("product_id")],
            limit=MEDIA_LIMIT,
        )
    }
    for item in media[:MEDIA_LIMIT]:
        product = facts.get(item.get("product_id"))
        url = item.get("url")
        if product is None or not url:
            continue
        outbound.append(
            _attach(
                OutboundMessage(
                    to=wa_id,
                    message_type="image",
                    link=url,
                    caption=_caption(product),
                ),
                state,
            )
        )
    return outbound


def _media(products: list[dict[str, Any]], limit: int = MEDIA_LIMIT) -> list[dict[str, str]]:
    return [
        {"type": "image", "url": product["primary_media_url"], "product_id": product["id"]}
        for product in products
        if product.get("primary_media_url")
    ][:limit]


def _product_text(product: dict[str, Any]) -> str:
    sizes = list(
        dict.fromkeys(
            variant.get("size") for variant in product.get("variants", []) if variant.get("size")
        )
    )
    size_text = f" Sizes: {' / '.join(sizes)}." if sizes else ""
    stock = product.get("available_qty")
    stock_text = f" Abhi {stock} {product['stock_unit']} available hain." if stock else ""
    return f"Solid choice 👌 {product['name']} {_price(product['price_paise'])} ki hai.{size_text}{stock_text}"


def _ordinal_product(
    db: Session, business_id: UUID, text: str, shown_ids: list[str]
) -> dict[str, Any] | None:
    request = interpret_discovery_message(text)
    if request.kind is not DiscoveryKind.SELECT_REFERENCE or request.reference_index is None:
        return None
    index = len(shown_ids) - 1 if request.reference_index == -1 else request.reference_index
    if not 0 <= index < len(shown_ids):
        return None
    products = product_facts(db, business_id, [shown_ids[index]], limit=1)
    return products[0] if products else None


def _semantic_shown_product(
    db: Session, business_id: UUID, text: str, shown_ids: list[str]
) -> dict[str, Any] | None:
    query_tokens = set(normalize_catalog_text(text).split()) - _REFERENCE_NOISE
    if not query_tokens:
        return None
    # Numeric/specification follow-ups refine the search rather than select a prior card.
    if query_tokens & {"watt", "watts", "volt", "volts", "amp", "amps"}:
        return None
    products = product_facts(db, business_id, shown_ids)
    scores: list[tuple[int, dict[str, Any]]] = []
    for product in products:
        candidate_tokens = set(normalize_catalog_text(product["name"]).split())
        aliases = db.scalars(
            select(ProductAlias.alias_text).where(
                ProductAlias.business_id == business_id,
                ProductAlias.product_id == UUID(product["id"]),
            )
        ).all()
        alias_scores = [
            len(query_tokens & set(normalize_catalog_text(alias).split())) for alias in aliases
        ]
        score = max([len(query_tokens & candidate_tokens), *alias_scores])
        if score:
            scores.append((score, product))
    scores.sort(key=lambda item: (-item[0], item[1]["name"]))
    if not scores or scores[0][0] < min(2, len(query_tokens)):
        return None
    if len(scores) > 1 and scores[0][0] == scores[1][0]:
        return None
    return scores[0][1]


def _variant_followup(
    product: dict[str, Any], text: str, previous: dict[str, Any]
) -> tuple[str, dict[str, Any]] | None:
    normalized = normalize_catalog_text(text)
    tokens = set(normalized.split())
    variants = product.get("variants", [])
    if not variants:
        return None

    if tokens & {"size", "sizes"}:
        sizes = list(
            dict.fromkeys(variant.get("size") for variant in variants if variant.get("size"))
        )
        if sizes:
            return (
                f"{product['name']} {' / '.join(sizes)} sizes mein available hai. Kaunsa chahiye?",
                previous,
            )

    selected_color = previous.get("selected_color")
    color_tokens = {
        normalize_catalog_text(v.get("color") or "") for v in variants if v.get("color")
    }

    explicit_color = None
    for ct in color_tokens:
        if ct and ct in tokens:
            explicit_color = ct
            break

    curr_color = explicit_color or (
        normalize_catalog_text(selected_color) if selected_color else None
    )

    size_matches = [
        v for v in variants if v.get("size") and normalize_catalog_text(v["size"]) in tokens
    ]

    if size_matches and len(tokens) <= 6:
        if curr_color:
            color_filtered = [
                v
                for v in size_matches
                if normalize_catalog_text(v.get("color") or "") == curr_color
            ]
            if color_filtered:
                size_matches = color_filtered

        available_matches = [v for v in size_matches if v.get("available")]
        requested_size = size_matches[0]["size"]

        if not available_matches:
            other_avail_sizes = list(
                dict.fromkeys(
                    v.get("size") for v in variants if v.get("available") and v.get("size")
                )
            )
            avail_str = (
                f" {' / '.join(other_avail_sizes)} available hain." if other_avail_sizes else ""
            )
            return (
                f"{requested_size} abhi out of stock hai.{avail_str} Doosra size ya option dikha du?",
                previous,
            )

        if len(available_matches) > 1 and not curr_color:
            colors = [v.get("color") for v in available_matches if v.get("color")]
            unique_colors = list(dict.fromkeys(colors))
            if len(unique_colors) > 1:
                opts = " ya ".join(f"{c} {requested_size}" for c in unique_colors)
                updated_state = {**previous, "selected_size": requested_size}
                return (f"Kaunsa color chahiye — {opts}?", updated_state)

        matched_var = available_matches[0]
        updated_state = {
            **previous,
            "selected_variant_id": matched_var["id"],
            "selected_size": matched_var.get("size"),
            "selected_color": matched_var.get("color"),
        }
        color_label = f"{matched_var.get('color')} " if matched_var.get("color") else ""
        return (
            f"Haan bhai, {color_label}{matched_var['size']} available hai 👍 Kitne chahiye?",
            updated_state,
        )

    if explicit_color and previous.get("selected_size"):
        sel_size = normalize_catalog_text(previous["selected_size"])
        color_size_matches = [
            v
            for v in variants
            if v.get("size")
            and normalize_catalog_text(v["size"]) == sel_size
            and normalize_catalog_text(v.get("color") or "") == explicit_color
            and v.get("available")
        ]
        if color_size_matches:
            matched_var = color_size_matches[0]
            updated_state = {
                **previous,
                "selected_variant_id": matched_var["id"],
                "selected_size": matched_var.get("size"),
                "selected_color": matched_var.get("color"),
            }
            color_label = f"{matched_var.get('color')} " if matched_var.get("color") else ""
            return (
                f"Done bhai! {color_label}{matched_var['size']} resolve ho gaya 👍 Kitne chahiye?",
                updated_state,
            )

    return None


def _is_payment_claim(text: str) -> bool:
    norm = normalize_catalog_text(text)
    patterns = [
        r"\b(payment|paisa|money)\s+(ho\s+gaya|kar\s+diya|done|sent|bhej\s+diya|ho\s+gayi)\b",
        r"\b(paid|payment\s+done|already\s+paid|done\s+payment|payment\s+sent|money\s+sent|amount\s+sent)\b",
        r"\b(paisa|money)\s+(bheja|bhej\s+diya|dal\s+diya)\b",
        r"\b(kar\s+diya\s+payment|payment\s+ho\s+gaya)\b",
    ]
    return any(re.search(p, norm) for p in patterns)


def _is_checkout_intent(text: str) -> bool:
    norm = normalize_catalog_text(text)
    patterns = [
        r"\b(checkout|check\s*out)\b",
        r"\b(payment|pay|link)\s+(karna|karo|bhejo|de|do|bhej|bhejo\s+na)\b",
        r"\b(proceed|kaha|kaise)\s+.*(payment|pay)\b",
        r"\b(pay|payment)\s+(ke\s+liye|kaise|kaha)\b",
        r"\b(order\s+place|place\s+order|buy\s+now)\b",
        r"\b(haan|yes)\s+(proceed|checkout)\b",
        r"\blink\s+(kaha|de|bhejo)\b",
        r"\bproceed\s+karo\b",
    ]
    return any(re.search(p, norm) for p in patterns)


def _handle_checkout_intent(
    db: Session,
    business_id: UUID,
    buyer_id: UUID,
    phone_number_id: str,
    wa_id: str,
    previous: dict[str, Any],
    inbound_message_id: str | None,
) -> list[OutboundMessage] | None:
    from app.api.routes.checkout import prepare_checkout_session
    from app.modules.commerce.cart_service import (
        add_to_cart,
        checkout_cart,
        get_or_create_active_cart,
    )
    from app.modules.commerce.models import Order, OrderItem
    from app.modules.commerce.sales_tools import _uuid

    print("DEBUG _handle_checkout_intent: started")
    # 1. Reuse existing pending order if present
    existing_order = db.scalar(
        select(Order)
        .where(
            Order.business_id == business_id,
            Order.buyer_id == buyer_id,
            Order.status == "pending_payment",
        )
        .order_by(Order.created_at.desc())
    )

    if existing_order:
        print("DEBUG _handle_checkout_intent: existing order found", existing_order.id)
        session_info = prepare_checkout_session(db, business_id, existing_order.id)
        payment_url = session_info["payment_url"]
        items = list(
            db.scalars(select(OrderItem).where(OrderItem.order_id == existing_order.id)).all()
        )
        total_paise = sum(item.unit_price_paise * item.quantity for item in items)
        total_rupees = total_paise / 100.0

        state = {
            **previous,
            "route": "checkout",
            "last_intent": "checkout",
            "order_id": str(existing_order.id),
            "checkout_session_id": session_info.get("checkout_session_id"),
            "payment_url": payment_url,
            "checkout_stage": "awaiting_payment",
            "tool_call": {"name": "checkout_cart", "arguments": {}},
        }
        text = (
            f"Done bhai 👍\nOrder ready hai.\n\nTotal: ₹{total_rupees:,.2f}".replace(".00", "")
            + "\n\n"
            f"Payment yahan kar sakte ho:\n{payment_url}\n\n"
            f"Payment confirm hote hi order confirm karke invoice yahin bhej dunga."
        )
        _persist_on_inbound(db, business_id, phone_number_id, wa_id, inbound_message_id, state)
        db.commit()
        return _messages(wa_id, text, state, db, business_id)

    # 2. No pending order. Check active cart / state
    cart = get_or_create_active_cart(db, business_id, buyer_id)
    selected_p_id = previous.get("selected_product_id")
    selected_v_id = previous.get("selected_variant_id")

    if cart.items and selected_v_id:
        for ci in cart.items:
            if not ci.variant_id and (
                not selected_p_id or str(ci.product_id) == str(selected_p_id)
            ):
                ci.variant_id = _uuid(selected_v_id)
        db.flush()

    if not cart.items:
        if not selected_p_id or not isinstance(selected_p_id, str):
            return None

        parsed_p_id = _uuid(selected_p_id)
        if not parsed_p_id:
            return None

        p_facts = product_facts(db, business_id, [selected_p_id], limit=1)
        if not p_facts:
            return None

        product = p_facts[0]
        variants = product.get("variants", [])

        if variants and not selected_v_id:
            if len(variants) == 1:
                selected_v_id = variants[0]["id"]
            else:
                free_sizes = [
                    v
                    for v in variants
                    if v.get("size")
                    and v["size"].lower() in {"free size", "free", "one size", "fs"}
                ]
                if len(free_sizes) == 1:
                    selected_v_id = free_sizes[0]["id"]
                else:
                    avail_sizes = [v["size"] for v in variants if v.get("size")]
                    size_str = ", ".join(avail_sizes) if avail_sizes else "available sizes"
                    text = f"Bhai pehle size select kar lo 👍 (Available: {size_str})"
                    state = {
                        **previous,
                        "route": "variant",
                        "last_intent": "ask_variant",
                        "tool_call": None,
                    }
                    _persist_on_inbound(
                        db, business_id, phone_number_id, wa_id, inbound_message_id, state
                    )
                    db.commit()
                    return _messages(wa_id, text, state, db, business_id)

        qty = int(previous.get("quantity", 1) or 1)
        add_res = add_to_cart(
            db,
            business_id,
            buyer_id,
            parsed_p_id,
            quantity=qty,
            idempotency_key=f"add_chk_{inbound_message_id or uuid4().hex[:8]}",
            variant_id=_uuid(selected_v_id) if selected_v_id else None,
        )
        if "error" in add_res:
            return None

    msg_id = inbound_message_id or f"chk_{uuid4().hex[:8]}"
    res = checkout_cart(
        db, business_id, buyer_id, delivery_address={}, idempotency_key=f"checkout_{msg_id}"
    )
    if "order_id" in res:
        order_id = UUID(res["order_id"])
        session_info = prepare_checkout_session(db, business_id, order_id)
        payment_url = session_info["payment_url"]

        items = list(db.scalars(select(OrderItem).where(OrderItem.order_id == order_id)).all())
        total_paise = sum(item.unit_price_paise * item.quantity for item in items)
        total_rupees = total_paise / 100.0

        state = {
            **previous,
            "route": "checkout",
            "last_intent": "checkout",
            "order_id": str(order_id),
            "checkout_session_id": session_info.get("checkout_session_id"),
            "payment_url": payment_url,
            "checkout_stage": "awaiting_payment",
            "tool_call": {"name": "checkout_cart", "arguments": {}},
        }
        text = (
            f"Done bhai 👍\nOrder ready hai.\n\nTotal: ₹{total_rupees:,.2f}".replace(".00", "")
            + "\n\n"
            f"Payment yahan kar sakte ho:\n{payment_url}\n\n"
            f"Payment confirm hote hi order confirm karke invoice yahin bhej dunga."
        )
        _persist_on_inbound(db, business_id, phone_number_id, wa_id, inbound_message_id, state)
        db.commit()
        return _messages(wa_id, text, state, db, business_id)

    return None


def process_customer_commerce_message(
    db: Session,
    business_id: UUID,
    phone_number_id: str,
    wa_id: str,
    text_body: str,
    *,
    inbound_message_id: str | None = None,
) -> list[OutboundMessage]:
    buyer = resolve_or_create_whatsapp_buyer(db, business_id, wa_id)
    previous = load_commerce_state(db, business_id, phone_number_id, wa_id)
    shown_ids = [value for value in previous["shown_product_ids"] if isinstance(value, str)]

    if _is_payment_claim(text_body):
        state = {**previous, "route": "chat", "last_intent": "payment_claim", "tool_call": None}
        text = "Samajh gaya. Payment confirm hote hi status automatically update ho jayega."
        _persist_on_inbound(db, business_id, phone_number_id, wa_id, inbound_message_id, state)
        return _messages(wa_id, text, state, db, business_id)

    if _is_checkout_intent(text_body):
        checkout_msgs = _handle_checkout_intent(
            db, business_id, buyer.id, phone_number_id, wa_id, previous, inbound_message_id
        )
        if checkout_msgs:
            return checkout_msgs

    selected = _ordinal_product(db, business_id, text_body, shown_ids)
    if selected is None:
        selected = _semantic_shown_product(db, business_id, text_body, shown_ids)
    if selected is not None:
        state = {
            **previous,
            "route": "product_details",
            "last_intent": "product_details",
            "selected_product_id": selected["id"],
            "shown_variant_ids": [variant["id"] for variant in selected["variants"]],
            "tool_call": {"name": "get_product", "arguments": {"product_id": selected["id"]}},
        }
        _persist_on_inbound(db, business_id, phone_number_id, wa_id, inbound_message_id, state)
        return _messages(
            wa_id, _product_text(selected), state, db, business_id, _media([selected], 1)
        )

    selected_id = previous.get("selected_product_id")
    if isinstance(selected_id, str):
        selected_products = product_facts(db, business_id, [selected_id], limit=1)
        if selected_products:
            variant_res = _variant_followup(selected_products[0], text_body, previous)
            if variant_res:
                variant_reply, new_state = variant_res
                state = {
                    **new_state,
                    "route": "variant",
                    "last_intent": "variant",
                    "tool_call": None,
                }
                _persist_on_inbound(
                    db, business_id, phone_number_id, wa_id, inbound_message_id, state
                )
                return _messages(wa_id, variant_reply, state, db, business_id)

    stable_message_id = (
        inbound_message_id
        or hashlib.sha256(
            f"{business_id}:{phone_number_id}:{wa_id}:{text_body}".encode()
        ).hexdigest()
    )
    turn = customer_salesperson_chat(
        db,
        business_id,
        buyer.id,
        phone_number_id,
        wa_id,
        text_body,
        previous,
        inbound_message_id=stable_message_id,
    )
    if turn is not None:
        state = {**previous, **turn.state_updates, "version": CONTEXT_VERSION}
        state["route"] = state.get("last_intent") or "chat"
        state["tool_call"] = turn.tool_call
        _persist_on_inbound(db, business_id, phone_number_id, wa_id, inbound_message_id, state)
        return _messages(
            wa_id,
            turn.text,
            state,
            db,
            business_id,
            turn.outbound_media,
        )

    from app.modules.commerce.discovery_service import (
        _legacy_process_customer_commerce_message,
    )

    fallback = _legacy_process_customer_commerce_message(
        db, business_id, phone_number_id, wa_id, text_body
    )
    fallback_state = previous
    if fallback and isinstance(getattr(fallback[0], "commerce_context", None), dict):
        legacy = fallback[0].commerce_context
        fallback_state = {
            **previous,
            "version": CONTEXT_VERSION,
            "route": legacy.get("route"),
            "last_intent": legacy.get("route"),
            "shown_product_ids": legacy.get("shown_product_ids", []),
            "selected_product_id": legacy.get("selected_product_id"),
            "tool_call": legacy.get("tool_call"),
        }
    facts = product_facts(db, business_id, fallback_state["shown_product_ids"])
    for message in fallback:
        message.commerce_context = fallback_state
    if fallback and facts:
        fallback.extend(_messages("", "", fallback_state, db, business_id, _media(facts))[1:])
        for message in fallback:
            message.to = wa_id
    _persist_on_inbound(db, business_id, phone_number_id, wa_id, inbound_message_id, fallback_state)
    return fallback
