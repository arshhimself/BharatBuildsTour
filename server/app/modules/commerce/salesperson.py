"""Number-B customer salesperson, isolated from the owner Manager."""
# ruff: noqa: E501

import json
import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.commerce.tools import build_commerce_tools
from app.modules.runs.conversation_graph import load_conversation_history

logger = logging.getLogger(__name__)

_PROMPT = """You are a friendly WhatsApp salesperson for a clothing store. Speak concise, natural Hinglish (2-4 sentences max). Be warm, confident, and helpful.

RULES:
- Use only provided tools to get product/store info. Never invent prices, stock, or discounts.
- NEVER say "backend", "database", "tool", "verification", "API", or any technical word.
- Keep responses brief. One idea at a time. No bullet lists.

FLOW:
1. For "kya hai", "dikhao", broad requests → use `browse_catalog` or `list_categories`.
2. For product name search → use `search_products`.
3. When customer shows interest in a product → use `get_product_variants` to show available sizes.
4. When customer picks a size or shows buy intent ("ek chahiye", "le lo", "M size chahiye") → use `add_to_cart` with the correct variant_id.
5. When customer says checkout/pay/ready → use `prepare_checkout` and share the URL.
6. For store info/policies → use `get_store_info`.

SIZE SELECTION: Always confirm size before add_to_cart. If customer says "M size" match it to the variant.
Do not add to cart without knowing the variant if the product has sizes.
"""


@dataclass(frozen=True)
class SalespersonTurn:
    text: str
    tool_call: dict[str, Any] | None
    shown_product_ids: list[str]
    selected_product_id: str | None
    cart_id: str | None
    order_id: str | None
    checkout_stage: str | None
    quantity: int | None


def _products(value: Any) -> list[dict]:
    if isinstance(value, list):
        return [
            item for item in value if isinstance(item, dict) and isinstance(item.get("id"), str)
        ]
    if isinstance(value, dict):
        return _products(value.get("products"))
    return []


def customer_salesperson_chat(
    db: Session,
    business_id: UUID,
    buyer_id: UUID,
    phone_number_id: str,
    wa_id: str,
    message: str,
    previous: dict[str, Any],
) -> SalespersonTurn | None:
    """Run the existing LangGraph/OpenAI stack; return None for deterministic fallback."""
    api_key = get_settings().openai_api_key.get_secret_value()
    if not api_key:
        return None
    try:
        history = load_conversation_history(db, wa_id, phone_number_id, business_id=business_id)
        messages = [
            HumanMessage(content=t["content"])
            if t["role"] == "user"
            else AIMessage(content=t["content"])
            for t in history
        ]
        state = {
            "shown_product_ids": previous.get("shown_product_ids", []),
            "selected_product_id": previous.get("selected_product_id"),
            "cart_id": previous.get("cart_id"),
            "order_id": previous.get("order_id"),
            "checkout_stage": previous.get("checkout_stage"),
            "quantity": previous.get("quantity", 1),
        }
        prompt = (
            _PROMPT
            + "\nTrusted conversation reference state (not customer supplied): "
            + json.dumps(state)
        )
        agent = create_react_agent(
            ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.2),
            build_commerce_tools(db, business_id, buyer_id),
            prompt=prompt,
        )
        result = agent.invoke({"messages": [*messages, HumanMessage(content=message)]})
        result_messages = result.get("messages", [])
        final = (result_messages[-1].content or "").strip() if result_messages else ""
        if not final:
            return None

        tool_call = None
        shown = state.get("shown_product_ids", [])
        selected = state.get("selected_product_id")
        cart_id = state.get("cart_id")
        order_id = state.get("order_id")
        checkout_stage = state.get("checkout_stage")
        quantity = state.get("quantity")

        tool_arguments = {
            call["id"]: call.get("args", {})
            for result_message in result_messages
            if isinstance(result_message, AIMessage)
            for call in result_message.tool_calls
            if isinstance(call.get("id"), str) and isinstance(call.get("args"), dict)
        }

        for item in result_messages:
            if not isinstance(item, ToolMessage):
                continue
            try:
                payload = (
                    json.loads(item.content) if isinstance(item.content, str) else item.content
                )
            except (TypeError, ValueError):
                continue
            tool_call = {"name": item.name, "arguments": tool_arguments.get(item.tool_call_id, {})}
            products = _products(payload)
            if products:
                shown = [product["id"] for product in products[:5]]
                selected = shown[0] if len(shown) == 1 else None

            # Tools updates state based on actions
            if (
                item.name == "get_product"
                and isinstance(payload, dict)
                and isinstance(payload.get("id"), str)
            ):
                selected = payload["id"]
            if item.name == "add_to_cart":
                args = tool_arguments.get(item.tool_call_id, {})
                if "product_id" in args:
                    selected = args["product_id"]
                if "quantity" in args:
                    quantity = args["quantity"]
                checkout_stage = "cart_added"
            if item.name == "prepare_checkout" and isinstance(payload, dict):
                checkout_stage = "checkout_prepared"
                if payload.get("order_id"):
                    order_id = payload["order_id"]

        logger.info(
            "customer salesperson completed",
            extra={
                "commerce_tool": tool_call["name"] if tool_call else None,
                "tool_success": bool(tool_call),
            },
        )
        return SalespersonTurn(
            final, tool_call, shown, selected, cart_id, order_id, checkout_stage, quantity
        )
    except Exception:
        logger.exception("customer salesperson failed; using deterministic discovery fallback")
        return None
