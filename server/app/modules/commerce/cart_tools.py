from typing import Any
from uuid import UUID

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


class AddToCartInput(BaseModel):
    quantity: int = Field(default=1, gt=0, description="Quantity to add")
    product_id: str | None = Field(
        default=None, description="Product UUID. Optional if product is already selected in state."
    )
    variant_id: str | None = Field(
        default=None, description="Variant UUID. Optional if variant is already selected in state."
    )


class UpdateCartQuantityInput(BaseModel):
    product_id: str = Field(description="Product UUID")
    quantity: int = Field(ge=0)


class RemoveFromCartInput(BaseModel):
    product_id: str = Field(description="Product UUID")


class CheckoutCartInput(BaseModel):
    delivery_address: dict = Field(
        default_factory=dict, description="Address fields like street, city, pin_code"
    )


def build_cart_tools(
    db: Session,
    business_id: UUID,
    buyer_id: UUID,
    message_id: str,
    context: dict[str, Any] | None = None,
) -> list[StructuredTool]:
    from sqlalchemy import select

    from app.modules.catalog.models import ProductVariant
    from app.modules.commerce.cart_service import (
        add_to_cart,
        checkout_cart,
        clear_cart,
        remove_from_cart,
        update_cart_quantity,
        view_cart,
    )

    ctx = context or {}

    def _add_to_cart(
        quantity: int = 1,
        product_id: str | None = None,
        variant_id: str | None = None,
    ) -> dict:
        resolved_product_str = product_id or ctx.get("selected_product_id")
        resolved_variant_str = variant_id or ctx.get("selected_variant_id")

        if not resolved_product_str:
            return {"error": "No product selected. Please select a product first."}

        try:
            parsed_product_id = UUID(resolved_product_str)
        except (ValueError, TypeError):
            return {"error": "Invalid product_id format"}

        parsed_variant_id: UUID | None = None
        if resolved_variant_str:
            try:
                parsed_variant_id = UUID(resolved_variant_str)
            except (ValueError, TypeError):
                return {"error": "Invalid variant_id format"}

        # Validate variant belongs to business and product if specified
        if parsed_variant_id:
            variant = db.scalar(
                select(ProductVariant).where(
                    ProductVariant.id == parsed_variant_id,
                    ProductVariant.business_id == business_id,
                    ProductVariant.product_id == parsed_product_id,
                    ProductVariant.active.is_(True),
                )
            )
            if not variant:
                return {"error": "Selected variant is invalid or inactive for this product."}

        return add_to_cart(
            db,
            business_id,
            buyer_id,
            parsed_product_id,
            quantity,
            idempotency_key=f"add_{message_id}_{parsed_product_id}_{parsed_variant_id or 'none'}_{quantity}",
            variant_id=parsed_variant_id,
        )

    def _update_cart_quantity(product_id: str, quantity: int) -> dict:
        try:
            parsed_id = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product_id format"}
        return update_cart_quantity(db, business_id, buyer_id, parsed_id, quantity)

    def _remove_from_cart(product_id: str) -> dict:
        try:
            parsed_id = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product_id format"}
        return remove_from_cart(db, business_id, buyer_id, parsed_id)

    def _clear_cart() -> dict:
        return clear_cart(db, business_id, buyer_id)

    def _view_cart() -> dict:
        return view_cart(db, business_id, buyer_id)

    def _checkout_cart(delivery_address: dict) -> dict:
        from app.api.routes.checkout import prepare_checkout_session

        res = checkout_cart(
            db, business_id, buyer_id, delivery_address, idempotency_key=f"checkout_{message_id}"
        )
        if "order_id" in res:
            order_id = UUID(res["order_id"])
            session_info = prepare_checkout_session(db, business_id, order_id)
            res["checkout_session_id"] = str(session_info.get("id", ""))
            res["payment_url"] = session_info["payment_url"]
        return res

    return [
        StructuredTool.from_function(
            func=_add_to_cart,
            name="add_to_cart",
            description="Add the selected product and variant to the buyer's active cart.",
            args_schema=AddToCartInput,
        ),
        StructuredTool.from_function(
            func=_update_cart_quantity,
            name="update_cart_quantity",
            description="Update the quantity of a product already in the cart. Set to 0 to remove.",
            args_schema=UpdateCartQuantityInput,
        ),
        StructuredTool.from_function(
            func=_remove_from_cart,
            name="remove_from_cart",
            description="Remove a specific product entirely from the active cart.",
            args_schema=RemoveFromCartInput,
        ),
        StructuredTool.from_function(
            func=_clear_cart,
            name="clear_cart",
            description="Remove all items from the active cart.",
        ),
        StructuredTool.from_function(
            func=_view_cart,
            name="view_cart",
            description="View all current items and totals in the active cart.",
        ),
        StructuredTool.from_function(
            func=_checkout_cart,
            name="checkout_cart",
            description="Convert the active cart into an Order pending payment.",
            args_schema=CheckoutCartInput,
        ),
    ]
