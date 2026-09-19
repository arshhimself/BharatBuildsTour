"""Cart and Order deterministic services for WhatsApp commerce."""

import hashlib
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.catalog.models import Product
from app.modules.commerce.models import Cart, CartItem, Order, OrderItem
from app.modules.inventory.models import Inventory
from app.modules.payments.models import IdempotencyKey


def claim_idempotency(
    db: Session, business_id: UUID, action: str, key: str, request_payload: str
) -> bool:
    """Returns True if this is a NEW request, False if it's a DUPLICATE."""
    request_sha256 = hashlib.sha256(request_payload.encode()).hexdigest()
    stmt = (
        insert(IdempotencyKey)
        .values(
            business_id=business_id,
            action=action,
            key=key,
            request_sha256=request_sha256,
            state="COMPLETED",
            response_status=200,
            response_reference={},
        )
        .on_conflict_do_nothing(index_elements=["business_id", "action", "key"])
        .returning(IdempotencyKey.id)
    )
    result = db.execute(stmt)
    return result.scalar() is not None


def get_or_create_active_cart(db: Session, business_id: UUID, buyer_id: UUID) -> Cart:
    # Use SELECT FOR UPDATE to prevent race conditions creating multiple active carts
    cart = db.scalar(
        select(Cart)
        .where(Cart.business_id == business_id, Cart.buyer_id == buyer_id, Cart.status == "active")
        .with_for_update()
    )
    if cart:
        return cart

    cart = Cart(business_id=business_id, buyer_id=buyer_id, status="active")
    db.add(cart)
    db.flush()
    return cart


def view_cart(db: Session, business_id: UUID, buyer_id: UUID) -> dict[str, Any]:
    cart = db.scalar(
        select(Cart).where(
            Cart.business_id == business_id, Cart.buyer_id == buyer_id, Cart.status == "active"
        )
    )
    if not cart:
        return {"items": [], "total_paise": 0}

    items = []
    total_paise = 0
    for ci in cart.items:
        product = db.scalar(
            select(Product).where(Product.id == ci.product_id, Product.business_id == business_id)
        )
        if product:
            unit_price = product.base_unit_price_paise
            size = None
            color = None
            variant_sku = product.sku

            if ci.variant_id:
                from app.modules.catalog.models import ProductVariant

                variant = db.scalar(
                    select(ProductVariant).where(ProductVariant.id == ci.variant_id)
                )
                if variant:
                    if variant.price_override_paise is not None:
                        unit_price = variant.price_override_paise
                    size = variant.size
                    color = variant.color
                    variant_sku = variant.sku

            line_total = unit_price * ci.quantity
            total_paise += line_total
            items.append(
                {
                    "product_id": str(product.id),
                    "variant_id": str(ci.variant_id) if ci.variant_id else None,
                    "sku": variant_sku,
                    "name": product.name,
                    "size": size,
                    "color": color,
                    "quantity": ci.quantity,
                    "unit_price_paise": unit_price,
                    "line_total_paise": line_total,
                }
            )
    return {"items": items, "total_paise": total_paise}


def add_to_cart(
    db: Session,
    business_id: UUID,
    buyer_id: UUID,
    product_id: UUID,
    quantity: int,
    idempotency_key: str,
    variant_id: UUID | None = None,
) -> dict[str, Any]:
    if quantity <= 0:
        return {"error": "Quantity must be positive."}

    if not claim_idempotency(
        db, business_id, "add_to_cart", idempotency_key, f"{product_id}-{variant_id}-{quantity}"
    ):
        return {"status": "duplicate_ignored"}

    # Verify product belongs to business and check inventory
    product = db.scalar(
        select(Product).where(Product.id == product_id, Product.business_id == business_id)
    )
    if not product:
        return {"error": "Product not found."}

    inventory = db.scalar(
        select(Inventory).where(Inventory.product_id == product_id).with_for_update()
    )

    cart = get_or_create_active_cart(db, business_id, buyer_id)

    # Check existing item
    cart_item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
            CartItem.variant_id == variant_id,
        )
    )

    new_quantity = quantity
    if cart_item:
        new_quantity += cart_item.quantity

    if inventory and inventory.on_hand_qty < new_quantity:
        return {"error": f"Insufficient stock. Only {inventory.on_hand_qty} available."}

    if cart_item:
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id, product_id=product_id, variant_id=variant_id, quantity=quantity
        )
        db.add(cart_item)

    db.flush()
    return {"status": "added", "new_quantity": new_quantity}


def update_cart_quantity(
    db: Session,
    business_id: UUID,
    buyer_id: UUID,
    product_id: UUID,
    quantity: int,
    variant_id: UUID | None = None,
) -> dict[str, Any]:
    if quantity < 0:
        return {"error": "Quantity cannot be negative."}

    cart = get_or_create_active_cart(db, business_id, buyer_id)
    cart_item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
            CartItem.variant_id == variant_id,
        )
    )

    if not cart_item:
        return {"error": "Item not in cart."}

    if quantity == 0:
        db.delete(cart_item)
        db.flush()
        return {"status": "removed"}

    inventory = db.scalar(
        select(Inventory).where(Inventory.product_id == product_id).with_for_update()
    )
    if inventory and inventory.on_hand_qty < quantity:
        return {"error": f"Insufficient stock. Only {inventory.on_hand_qty} available."}

    cart_item.quantity = quantity
    db.flush()
    return {"status": "updated", "new_quantity": quantity}


def remove_from_cart(
    db: Session, business_id: UUID, buyer_id: UUID, product_id: UUID, variant_id: UUID | None = None
) -> dict[str, Any]:
    cart = get_or_create_active_cart(db, business_id, buyer_id)
    cart_item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
            CartItem.variant_id == variant_id,
        )
    )
    if cart_item:
        db.delete(cart_item)
        db.flush()
        return {"status": "removed"}
    return {"status": "not_found"}


def clear_cart(db: Session, business_id: UUID, buyer_id: UUID) -> dict[str, Any]:
    cart = db.scalar(
        select(Cart)
        .where(Cart.business_id == business_id, Cart.buyer_id == buyer_id, Cart.status == "active")
        .with_for_update()
    )
    if cart:
        db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        db.flush()
    return {"status": "cleared"}


def checkout_cart(
    db: Session,
    business_id: UUID,
    buyer_id: UUID,
    delivery_address: dict[str, Any],
    idempotency_key: str,
) -> dict[str, Any]:
    if not claim_idempotency(
        db, business_id, "checkout_cart", idempotency_key, str(delivery_address)
    ):
        # Duplicate request, return existing order if possible, or just a duplicate status
        # A robust system would store the created order ID in response_reference
        return {"status": "duplicate_ignored"}

    cart = db.scalar(
        select(Cart)
        .where(Cart.business_id == business_id, Cart.buyer_id == buyer_id, Cart.status == "active")
        .with_for_update()
    )

    if not cart or not cart.items:
        return {"error": "Cart is empty or not found."}

    order = Order(
        business_id=business_id,
        buyer_id=buyer_id,
        status="pending_payment",
        delivery_address=delivery_address,
    )
    db.add(order)
    db.flush()

    for ci in cart.items:
        product = db.scalar(select(Product).where(Product.id == ci.product_id).with_for_update())
        inventory = db.scalar(
            select(Inventory).where(Inventory.product_id == ci.product_id).with_for_update()
        )

        if not product:
            return {"error": f"Product {ci.product_id} no longer exists."}

        if inventory and inventory.on_hand_qty < ci.quantity:
            return {
                "error": f"Insufficient stock for {product.name}. Only {inventory.on_hand_qty} available."
            }

        unit_price = product.base_unit_price_paise
        sku = product.sku
        size = None
        color = None

        if ci.variant_id:
            from app.modules.catalog.models import ProductVariant

            variant = db.scalar(select(ProductVariant).where(ProductVariant.id == ci.variant_id))
            if variant:
                if variant.price_override_paise is not None:
                    unit_price = variant.price_override_paise
                sku = variant.sku
                size = variant.size
                color = variant.color

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            variant_id=ci.variant_id,
            sku_snapshot=sku,
            name_snapshot=product.name,
            size_snapshot=size,
            color_snapshot=color,
            unit_price_paise=unit_price,
            quantity=ci.quantity,
        )
        db.add(order_item)

    cart.status = "converted"
    db.flush()
    return {"status": "success", "order_id": str(order.id)}
