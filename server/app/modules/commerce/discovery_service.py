"""Tenant-safe deterministic catalog discovery for customer WhatsApp commerce."""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.commerce.discovery import DiscoveryKind, interpret_discovery_message
from app.modules.commerce.tools import build_commerce_tools
from app.modules.identity.service import resolve_or_create_whatsapp_buyer
from app.modules.runs.service import OutboundMessage
from app.modules.whatsapp.models import WhatsAppMessage

logger = logging.getLogger(__name__)

_RESULT_LIMIT = 5
_CONTEXT_VERSION = 1


def _load_reference_state(
    db: Session,
    business_id: UUID,
    phone_number_id: str,
    wa_id: str,
) -> dict[str, Any]:
    rows = db.scalars(
        select(WhatsAppMessage)
        .where(
            WhatsAppMessage.business_id == business_id,
            WhatsAppMessage.phone_number_id == phone_number_id,
            WhatsAppMessage.wa_id == wa_id,
            WhatsAppMessage.direction == "out",
        )
        .order_by(WhatsAppMessage.created_at.desc(), WhatsAppMessage.id.desc())
        .limit(12)
    )
    for row in rows:
        context = (row.payload or {}).get("commerce_context")
        if isinstance(context, dict) and context.get("version") in {_CONTEXT_VERSION, 2}:
            return context
    return {}


def _context(
    route: DiscoveryKind,
    *,
    tool_name: str | None = None,
    arguments: dict[str, Any] | None = None,
    shown_product_ids: list[str] | None = None,
    selected_product_id: str | None = None,
) -> dict[str, Any]:
    return {
        "version": _CONTEXT_VERSION,
        "route": route.value,
        "tool_call": (
            {"name": tool_name, "arguments": arguments or {}} if tool_name is not None else None
        ),
        "shown_product_ids": shown_product_ids or [],
        "selected_product_id": selected_product_id,
    }


def _outbound(to: str, text: str, context: dict[str, Any]) -> OutboundMessage:
    message = OutboundMessage(to=to, text=text)
    message.commerce_context = context
    return message


def _price_text(price_paise: int) -> str:
    return f"₹{price_paise / 100:,.2f}"


def _gst_text(gst_rate_bps: int) -> str:
    return f"{gst_rate_bps / 100:g}%"


def _product_list_text(products: list[dict], *, intro: str) -> str:
    lines = [intro]
    for index, product in enumerate(products, start=1):
        lines.append(
            f"{index}. {product['name']} ({product['sku']}) — "
            f"{_price_text(product['price_paise'])} + GST {_gst_text(product['gst_rate_bps'])}"
        )
    lines.append("Kisi option ka number ya naam bhejo; main details aur stock check kar dunga.")
    return "\n".join(lines)


def _catalog_result(
    wa_id: str,
    route: DiscoveryKind,
    products: list[dict],
    *,
    tool_name: str,
    arguments: dict[str, Any],
    intro: str,
    empty_text: str,
) -> OutboundMessage:
    visible = products[:_RESULT_LIMIT]
    context = _context(
        route,
        tool_name=tool_name,
        arguments=arguments,
        shown_product_ids=[item["id"] for item in visible],
        selected_product_id=visible[0]["id"] if len(visible) == 1 else None,
    )
    if not visible:
        return _outbound(wa_id, empty_text, context)
    return _outbound(wa_id, _product_list_text(visible, intro=intro), context)


def _legacy_process_customer_commerce_message(
    db: Session,
    business_id: UUID,
    phone_number_id: str,
    wa_id: str,
    text_body: str,
) -> list[OutboundMessage]:
    """Resolve a Lead and execute read-only discovery using trusted tenant tools."""
    resolve_or_create_whatsapp_buyer(db, business_id, wa_id)
    request = interpret_discovery_message(text_body)
    tools = {tool.name: tool for tool in build_commerce_tools(db, business_id)}
    previous = _load_reference_state(db, business_id, phone_number_id, wa_id)

    logger.info(
        "Commerce discovery route selected",
        extra={
            "commerce_route": request.kind.value,
            "commerce_tool": {
                DiscoveryKind.BROWSE: "browse_catalog",
                DiscoveryKind.SEARCH: "search_products",
                DiscoveryKind.PRICE_FILTER: "filter_products_by_price",
                DiscoveryKind.SELECT_REFERENCE: "get_product",
                DiscoveryKind.INVENTORY: "check_inventory",
            }.get(request.kind),
        },
    )

    if request.kind is DiscoveryKind.BROWSE:
        arguments = {"limit": _RESULT_LIMIT}
        products = tools["browse_catalog"].invoke(arguments)
        return [
            _catalog_result(
                wa_id,
                request.kind,
                products,
                tool_name="browse_catalog",
                arguments=arguments,
                intro="Bilkul! Hamare real catalog se kuch options:",
                empty_text="Abhi active catalog products available nahi hain.",
            )
        ]

    if request.kind is DiscoveryKind.SEARCH:
        arguments = {"query": request.query}
        products = tools["search_products"].invoke(arguments)
        return [
            _catalog_result(
                wa_id,
                request.kind,
                products,
                tool_name="search_products",
                arguments=arguments,
                intro=f'"{request.query}" ke liye ye real matches mile:',
                empty_text=(
                    f'Mujhe catalog mein "{request.query}" nahi mila. '
                    "Koi category, use-case ya doosra product naam batao."
                ),
            )
        ]

    if request.kind is DiscoveryKind.PRICE_FILTER:
        arguments = {
            "min_price_paise": request.min_price_paise,
            "max_price_paise": request.max_price_paise,
            "limit": _RESULT_LIMIT,
        }
        products = tools["filter_products_by_price"].invoke(arguments)
        return [
            _catalog_result(
                wa_id,
                request.kind,
                products,
                tool_name="filter_products_by_price",
                arguments=arguments,
                intro="Aapke budget ke andar ye real options mile:",
                empty_text="Is budget range mein koi active product nahi mila.",
            )
        ]

    shown_ids = [value for value in previous.get("shown_product_ids", []) if isinstance(value, str)]
    selected_id = previous.get("selected_product_id")
    selected_id = selected_id if isinstance(selected_id, str) else None

    if request.kind is DiscoveryKind.SELECT_REFERENCE:
        index = request.reference_index
        if index is None or not shown_ids:
            return [
                _outbound(
                    wa_id,
                    "Pehle products dekh lete hain—product naam ya category batao.",
                    _context(request.kind),
                )
            ]
        resolved_index = len(shown_ids) - 1 if index == -1 else index
        if resolved_index < 0 or resolved_index >= len(shown_ids):
            return [
                _outbound(
                    wa_id,
                    "Woh option list mein nahi hai. Dikhaye gaye option ka valid number bhejo.",
                    _context(request.kind, shown_product_ids=shown_ids),
                )
            ]
        arguments = {"product_id": shown_ids[resolved_index]}
        product = tools["get_product"].invoke(arguments)
        if "error" in product:
            return [
                _outbound(
                    wa_id,
                    "Woh product ab active catalog mein available nahi hai.",
                    _context(
                        request.kind,
                        tool_name="get_product",
                        arguments=arguments,
                        shown_product_ids=shown_ids,
                    ),
                )
            ]
        return [
            _outbound(
                wa_id,
                (
                    f"Selected: {product['name']} ({product['sku']}) — "
                    f"{_price_text(product['price_paise'])} + "
                    f"GST {_gst_text(product['gst_rate_bps'])}. Stock check karun?"
                ),
                _context(
                    request.kind,
                    tool_name="get_product",
                    arguments=arguments,
                    shown_product_ids=shown_ids,
                    selected_product_id=product["id"],
                ),
            )
        ]

    if request.kind is DiscoveryKind.INVENTORY:
        if selected_id is None and len(shown_ids) == 1:
            selected_id = shown_ids[0]
        if selected_id is None:
            return [
                _outbound(
                    wa_id,
                    "Kis product ka stock check karna hai? Naam ya option number bhejo.",
                    _context(request.kind, shown_product_ids=shown_ids),
                )
            ]
        product_arguments = {"product_id": selected_id}
        product = tools["get_product"].invoke(product_arguments)
        if "error" in product:
            return [
                _outbound(
                    wa_id,
                    "Selected product ab active catalog mein nahi hai.",
                    _context(
                        request.kind,
                        tool_name="get_product",
                        arguments=product_arguments,
                        shown_product_ids=shown_ids,
                    ),
                )
            ]
        arguments = {"product_id": selected_id, "requested_qty": 1}
        stock = tools["check_inventory"].invoke(arguments)
        if "error" in stock:
            text = "Inventory abhi verify nahi ho pa rahi. Thodi der baad try karein."
        else:
            text = (
                f"{product['name']} ka status {stock['status']} hai; "
                f"available {stock['available_qty']} {stock['stock_unit']}."
            )
        return [
            _outbound(
                wa_id,
                text,
                _context(
                    request.kind,
                    tool_name="check_inventory",
                    arguments=arguments,
                    shown_product_ids=shown_ids,
                    selected_product_id=selected_id,
                ),
            )
        ]

    normalized = text_body.casefold()
    if "payment" in normalized or "paid" in normalized:
        text = (
            "Payment confirmation backend verification ke baad hi hoti hai. "
            "Verified status milte hi main confirm karunga."
        )
    else:
        text = (
            "Hello! Main real catalog, price aur stock mein help kar sakta hoon. "
            "Aap product naam bolo ya 'products dikhao' likho."
        )
    return [_outbound(wa_id, text, _context(DiscoveryKind.CHAT))]


def process_customer_commerce_message(
    db: Session,
    business_id: UUID,
    phone_number_id: str,
    wa_id: str,
    text_body: str,
    *,
    inbound_message_id: str | None = None,
) -> list[OutboundMessage]:
    """Use the production customer salesperson; retain this module as compatibility API."""
    from app.modules.commerce.customer_service import process_customer_commerce_message as process

    return process(
        db,
        business_id,
        phone_number_id,
        wa_id,
        text_body,
        inbound_message_id=inbound_message_id,
    )
