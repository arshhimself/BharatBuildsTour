from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.api.commercial import CommercialError
from app.modules.catalog.models import Product
from app.modules.catalog.normalization import normalize_catalog_text
from app.modules.inventory import repository
from app.modules.inventory.schemas import (
    InventoryCheckIn,
    InventoryCheckOut,
    StockStatus,
    SubstituteOut,
)


def check_stock(
    session: Session,
    business_id: UUID,
    request: InventoryCheckIn,
    get_reserved_qty: Callable[[Session, UUID, UUID], float] | None = None,
) -> InventoryCheckOut:
    product = repository.get_active_product(session, business_id, request.product_id)
    if product is None:
        raise CommercialError(404, "NOT_FOUND", "Product not found.")
    inventory = repository.get_inventory(session, business_id, product.id)
    if inventory is None:
        raise CommercialError(500, "INTERNAL_ERROR", "Inventory record missing for product.")

    requested = _stock_quantity(product, request)
    on_hand = float(inventory.on_hand_qty)
    reserved = get_reserved_qty(session, business_id, product.id) if get_reserved_qty else 0.0
    available = max(0.0, on_hand - reserved)
    available_dec = Decimal(str(available)).quantize(Decimal("0.001"))

    if available_dec == 0:
        status = StockStatus.OUT_OF_STOCK
    elif available_dec < requested:
        status = StockStatus.INSUFFICIENT_STOCK
    elif (
        inventory.reorder_threshold is not None
        and available_dec - requested <= inventory.reorder_threshold
    ):
        status = StockStatus.LOW_STOCK
    else:
        status = StockStatus.AVAILABLE

    substitutes: list[SubstituteOut] = []
    if status in {StockStatus.OUT_OF_STOCK, StockStatus.INSUFFICIENT_STOCK}:
        for relationship, alternative, alternative_stock in repository.ranked_substitutes(
            session, business_id, product.id
        ):
            if alternative.stock_unit != product.stock_unit:
                continue
            if alternative_stock.on_hand_qty < requested:
                continue
            substitutes.append(
                SubstituteOut(
                    product_id=alternative.id,
                    sku=alternative.sku,
                    name=alternative.name,
                    rank=relationship.rank,
                    reason=relationship.reason,
                )
            )

    return InventoryCheckOut(
        status=status,
        product_id=product.id,
        requested_qty=requested,
        stock_unit=product.stock_unit,
        on_hand_qty=Decimal(str(on_hand)),
        available_qty=available_dec,
        checked_at=datetime.now(UTC),
        substitutes=substitutes,
    )


def _stock_quantity(product: Product, request: InventoryCheckIn) -> Decimal:
    requested = Decimal(request.requested_qty)
    if request.requested_unit is None:
        # Contracted inventory quantities are in the canonical stock unit.
        unit = product.stock_unit
    else:
        unit = request.requested_unit
    normalized_unit = normalize_catalog_text(unit)
    stock_unit = normalize_catalog_text(product.stock_unit)
    sellable_unit = normalize_catalog_text(product.sellable_unit)
    if normalized_unit == stock_unit:
        result = requested
    elif normalized_unit == sellable_unit:
        if product.indivisible and requested != requested.to_integral_value():
            raise CommercialError(422, "VALIDATION_ERROR", "Product quantity must be whole units.")
        # Explicit product pack_size is the only supported conversion metadata.
        result = requested * product.pack_size
    else:
        raise CommercialError(422, "VALIDATION_ERROR", "Requested unit is not supported.")
    if result != result.quantize(Decimal("0.001")) or result >= Decimal("1000000000000000"):
        raise CommercialError(
            422, "VALIDATION_ERROR", "Converted quantity exceeds stock precision."
        )
    if product.indivisible and result != result.to_integral_value():
        raise CommercialError(422, "VALIDATION_ERROR", "Product quantity must be whole units.")
    return result.quantize(Decimal("0.001"))
