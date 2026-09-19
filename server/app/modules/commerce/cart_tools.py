from uuid import UUID

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


class AddToCartInput(BaseModel):
    product_id: str = Field(description="Product UUID")
    quantity: int = Field(default=1, gt=0)


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
    db: Session, business_id: UUID, buyer_id: UUID, message_id: str
) -> list[StructuredTool]:
    from app.modules.commerce.cart_service import (
        add_to_cart,
        checkout_cart,
        clear_cart,
        remove_from_cart,
        update_cart_quantity,
        view_cart,
    )

    def _add_to_cart(product_id: str, quantity: int = 1) -> dict:
        try:
            parsed_id = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product_id format"}
        return add_to_cart(
            db,
            business_id,
            buyer_id,
            parsed_id,
            quantity,
            idempotency_key=f"add_{message_id}_{product_id}",
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
        return checkout_cart(
            db, business_id, buyer_id, delivery_address, idempotency_key=f"checkout_{message_id}"
        )

    return [
        StructuredTool.from_function(
            func=_add_to_cart,
            name="add_to_cart",
            description="Add a specific product to the buyer's active cart.",
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
