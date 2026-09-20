"""Cart and Order deterministic services for WhatsApp commerce."""

import hashlib
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.catalog.models import Product, ProductVariant
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
    inserted_id = db.scalar(stmt)
    return inserted_id is not None


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
            line_total = product.price_paise * ci.quantity
            total_paise += line_total
            items.append(
                {
                    "product_id": str(product.id),
                    "sku": product.sku,
                    "name": product.name,
                    "quantity": ci.quantity,
                    "unit_price_paise": product.price_paise,
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
        db, business_id, "add_to_cart", idempotency_key, str(product_id) + str(quantity)
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
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
    )

    new_quantity = quantity
    if cart_item:
        new_quantity += cart_item.quantity

    if inventory and inventory.quantity_available < new_quantity:
        return {"error": f"Insufficient stock. Only {inventory.quantity_available} available."}

    if cart_item:
        cart_item.quantity = new_quantity
        if variant_id:
            cart_item.variant_id = variant_id
    else:
        cart_item = CartItem(
            cart_id=cart.id, product_id=product_id, variant_id=variant_id, quantity=quantity
        )
        db.add(cart_item)

    db.flush()
    db.expire(cart, ["items"])
    return {"status": "added", "new_quantity": new_quantity}


def update_cart_quantity(
    db: Session, business_id: UUID, buyer_id: UUID, product_id: UUID, quantity: int
) -> dict[str, Any]:
    if quantity < 0:
        return {"error": "Quantity cannot be negative."}

    cart = get_or_create_active_cart(db, business_id, buyer_id)
    cart_item = db.scalar(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
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
    if inventory and inventory.quantity_available < quantity:
        return {"error": f"Insufficient stock. Only {inventory.quantity_available} available."}

    cart_item.quantity = quantity
    db.flush()
    return {"status": "updated", "new_quantity": quantity}


def remove_from_cart(
    db: Session, business_id: UUID, buyer_id: UUID, product_id: UUID
) -> dict[str, Any]:
    cart = get_or_create_active_cart(db, business_id, buyer_id)
    cart_item = db.scalar(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
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

    if cart:
        db.expire(cart, ["items"])

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

        has_active_variants = db.scalar(
            select(ProductVariant.id)
            .where(
                ProductVariant.business_id == business_id,
                ProductVariant.product_id == ci.product_id,
                ProductVariant.active.is_(True),
            )
            .limit(1)
        )
        if has_active_variants and not ci.variant_id:
            return {"error": f"Please select a size/variant for {product.name} before checkout."}

        if inventory and inventory.quantity_available < ci.quantity:
            return {"error": f"Insufficient stock for {product.name}."}

        unit_price = product.price_paise
        sku_snap = product.sku
        size_snap = None
        color_snap = None

        if ci.variant_id:
            variant = db.scalar(
                select(ProductVariant).where(
                    ProductVariant.id == ci.variant_id,
                    ProductVariant.business_id == business_id,
                    ProductVariant.product_id == ci.product_id,
                    ProductVariant.active.is_(True),
                )
            )
            if not variant:
                return {"error": f"Selected variant for {product.name} is no longer active."}

            variant_inv = db.scalar(
                select(Inventory)
                .where(
                    Inventory.business_id == business_id,
                    Inventory.variant_id == ci.variant_id,
                )
                .with_for_update()
            )
            if variant_inv and variant_inv.quantity_available < ci.quantity:
                return {
                    "error": f"Insufficient stock for {product.name} ({variant.size or variant.color}). Only {variant_inv.quantity_available} available."
                }

            if variant.price_override_paise is not None:
                unit_price = variant.price_override_paise
            sku_snap = variant.sku
            size_snap = variant.size
            color_snap = variant.color

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            variant_id=ci.variant_id,
            sku_snapshot=sku_snap,
            name_snapshot=product.name,
            size_snapshot=size_snap,
            color_snapshot=color_snap,
            unit_price_paise=unit_price,
            quantity=ci.quantity,
        )
        db.add(order_item)

    cart.status = "converted"
    db.flush()
    return {"status": "success", "order_id": str(order.id)}
