from uuid import UUID

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.modules.catalog.service import (
    filter_products_by_price,
    get_product,
    get_products,
    search_products,
)
from app.modules.inventory.schemas import InventoryCheckIn
from app.modules.inventory.service import check_stock


class BrowseCatalogInput(BaseModel):
    limit: int = Field(default=5, ge=1, le=20)


class SearchProductsInput(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=120,
        description="Clean product terms only, never the full customer sentence",
    )


class FilterProductsInput(BaseModel):
    min_price_paise: int | None = Field(default=None, ge=0)
    max_price_paise: int | None = Field(default=None, ge=0)
    limit: int = Field(default=5, ge=1, le=20)


class GetProductInput(BaseModel):
    product_id: str = Field(description="Product UUID returned by another catalog tool")


class CheckInventoryInput(BaseModel):
    product_id: str = Field(description="Product UUID returned by a catalog tool")
    requested_qty: float = Field(gt=0, description="The quantity requested")
    requested_unit: str | None = Field(
        default=None, description="The unit requested (e.g. 'box', 'piece')"
    )


def _product_fact(product) -> dict:
    return {
        "id": str(product.product_id),
        "name": product.name,
        "sku": product.sku,
        "sellable_unit": product.sellable_unit,
        "stock_unit": product.stock_unit,
        "price_paise": product.base_unit_price_paise,
        "gst_rate_bps": product.gst_rate_bps,
    }


def get_store_info(db: Session, business_id: UUID) -> dict:
    """Fetch business details, address, support contact, opening hours, delivery info, and return policy."""
    from sqlalchemy import select

    from app.modules.identity.models import Business, StoreProfile

    business = db.scalar(select(Business).where(Business.id == business_id))
    profile = db.scalar(select(StoreProfile).where(StoreProfile.business_id == business_id))
    if not business:
        return {"error": "Store not found"}
    return {
        "display_name": business.display_name,
        "name": business.display_name,
        "description": profile.description if profile else None,
        "store_type": profile.store_type if profile else None,
        "address_line": profile.address_line if profile else business.billing_address,
        "city": profile.city if profile else None,
        "support_number": profile.support_number if profile else None,
        "opening_hours": profile.opening_hours if profile else "9 AM - 8 PM",
        "delivery_info": profile.delivery_info
        if profile
        else "Free delivery above ₹999 within 2-3 business days",
        "return_policy": profile.return_policy if profile else "7-day easy return policy",
    }


def _build_legacy_commerce_tools(db: Session, business_id: UUID) -> list[StructuredTool]:
    """Build read-only commerce tools bound to trusted server-side tenant context."""

    def _browse_catalog(limit: int = 5) -> list[dict]:
        products = get_products(
            db,
            business_id,
            include_inactive=False,
            limit=limit,
            offset=0,
        )
        return [_product_fact(product) for product in products]

    def _search_products(query: str) -> list[dict]:
        return [_product_fact(product) for product in search_products(db, business_id, query)]

    def _filter_products(
        min_price_paise: int | None = None,
        max_price_paise: int | None = None,
        limit: int = 5,
    ) -> list[dict]:
        products = filter_products_by_price(
            db,
            business_id,
            min_price_paise=min_price_paise,
            max_price_paise=max_price_paise,
            limit=limit,
        )
        return [_product_fact(product) for product in products]

    def _get_product(product_id: str) -> dict:
        try:
            parsed_id = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product_id format"}
        product = get_product(db, business_id, parsed_id)
        return _product_fact(product) if product is not None else {"error": "Product not found"}

    def _check_inventory(
        product_id: str, requested_qty: float, requested_unit: str | None = None
    ) -> dict:
        try:
            parsed_id = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product_id format"}

        try:
            result = check_stock(
                db,
                business_id,
                InventoryCheckIn(
                    business_id=business_id,
                    run_id="commerce-discovery-check",
                    product_id=parsed_id,
                    requested_qty=str(requested_qty),
                    requested_unit=requested_unit,
                ),
            )
            return {
                "product_id": str(result.product_id),
                "status": result.status.value,
                "available_qty": str(result.available_qty),
                "stock_unit": result.stock_unit,
                "substitutes": [
                    {"id": str(item.product_id), "name": item.name, "reason": item.reason}
                    for item in result.substitutes
                ],
            }
        except Exception as exc:
            return {"error": str(exc)}

    def _get_store_info() -> dict:
        return get_store_info(db, business_id)

    class GetStoreInfoInput(BaseModel):
        pass

    return [
        StructuredTool.from_function(
            func=_browse_catalog,
            name="browse_catalog",
            description=(
                "List real active tenant products for broad discovery requests such as "
                "'what do you sell?'. Do not pass customer prose as a product query."
            ),
            args_schema=BrowseCatalogInput,
        ),
        StructuredTool.from_function(
            func=_search_products,
            name="search_products",
            description=(
                "Search real active tenant products by a clean product name, SKU, or alias. "
                "The query must contain only product terms such as 'LED' or '12 watt LED'."
            ),
            args_schema=SearchProductsInput,
        ),
        StructuredTool.from_function(
            func=_filter_products,
            name="filter_products_by_price",
            description="List real active tenant products within authoritative price bounds.",
            args_schema=FilterProductsInput,
        ),
        StructuredTool.from_function(
            func=_get_product,
            name="get_product",
            description="Revalidate one product UUID previously returned by this tenant's catalog.",
            args_schema=GetProductInput,
        ),
        StructuredTool.from_function(
            func=_check_inventory,
            name="check_inventory",
            description="Read authoritative inventory for a product returned by a catalog tool.",
            args_schema=CheckInventoryInput,
        ),
        StructuredTool.from_function(
            func=_get_store_info,
            name="get_store_info",
            description="Fetch business details, address, support contact, opening hours, delivery info, and return policy.",
            args_schema=GetStoreInfoInput,
        ),
    ]


def build_commerce_tools(
    db: Session,
    business_id: UUID,
    buyer_id: UUID | None = None,
    message_id: str = "commerce-turn",
    context: dict | None = None,
) -> list[StructuredTool]:
    """Build Number-B tools with trusted server-side tenant and buyer context."""
    from app.modules.commerce.sales_tools import build_customer_sales_tools

    return build_customer_sales_tools(
        db,
        business_id,
        buyer_id=buyer_id,
        message_id=message_id,
        context=context,
    )
