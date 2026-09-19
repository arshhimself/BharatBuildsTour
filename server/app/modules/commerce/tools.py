from uuid import UUID

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.modules.catalog.service import (
    browse_category,
    filter_products_by_price,
    get_product,
    get_products,
    list_categories,
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


class BrowseCategoryInput(BaseModel):
    category_name: str = Field(min_length=1, max_length=120, description="A real category name")
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


def build_commerce_tools(db: Session, business_id: UUID) -> list[StructuredTool]:
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

    def _list_categories() -> list[dict]:
        return list_categories(db, business_id)

    def _browse_category(category_name: str, limit: int = 5) -> dict:
        category, products = browse_category(db, business_id, category_name, limit=limit)
        if category is None:
            return {"error": "Category not found"}
        return {"category": category, "products": [_product_fact(product) for product in products]}

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

    return [
        StructuredTool.from_function(
            func=_list_categories,
            name="list_categories",
            description="List real categories for this tenant before discussing a category.",
        ),
        StructuredTool.from_function(
            func=_browse_category,
            name="browse_category",
            description="Resolve one real category name and list its active tenant products.",
            args_schema=BrowseCategoryInput,
        ),
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
    ]
