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
        "has_variants": True,  # variants are fetched via get_product_variants tool
    }


class GetProductVariantsInput(BaseModel):
    product_id: str = Field(description="Product UUID returned by a catalog tool")


class AddToCartInput(BaseModel):
    product_id: str = Field(description="Product UUID returned by a catalog tool")
    quantity: int = Field(gt=0, description="The quantity requested")
    variant_id: str | None = Field(
        default=None, description="Variant UUID returned by get_product_variants"
    )


def build_commerce_tools(db: Session, business_id: UUID, buyer_id: UUID) -> list[StructuredTool]:
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

    def _get_store_info() -> dict:
        from sqlalchemy import select

        from app.modules.identity.models import StoreProfile

        profile = db.scalar(select(StoreProfile).where(StoreProfile.business_id == business_id))
        if not profile:
            return {"error": "Store profile not found"}
        return {
            "display_name": profile.display_name,
            "description": profile.description,
            "store_type": profile.store_type,
            "city": profile.city,
            "support_number": profile.support_number,
            "opening_hours": profile.opening_hours,
            "delivery_info": profile.delivery_info,
            "return_policy": profile.return_policy,
        }

    def _get_product_variants(product_id: str) -> dict:
        from sqlalchemy import select

        from app.modules.catalog.models import ProductVariant

        try:
            parsed_id = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product_id format"}
        variants = db.scalars(
            select(ProductVariant).where(
                ProductVariant.product_id == parsed_id,
                ProductVariant.business_id == business_id,
                ProductVariant.active.is_(True),
            )
        ).all()
        return {
            "product_id": product_id,
            "variants": [
                {
                    "id": str(v.id),
                    "sku": v.sku,
                    "size": v.size,
                    "color": v.color,
                    "price_paise": v.price_override_paise,  # None = use product base price
                }
                for v in variants
            ],
        }

    def _add_to_cart(product_id: str, quantity: int, variant_id: str | None = None) -> dict:
        import uuid

        from app.modules.commerce.cart_service import add_to_cart

        try:
            parsed_id = UUID(product_id)
        except ValueError:
            return {"error": "Invalid product_id format"}

        parsed_variant_id = None
        if variant_id:
            try:
                parsed_variant_id = UUID(variant_id)
            except ValueError:
                return {"error": "Invalid variant_id format"}

        idem_key = f"demo_add_{uuid.uuid4().hex[:8]}"
        res = add_to_cart(
            db, business_id, buyer_id, parsed_id, quantity, idem_key, parsed_variant_id
        )
        if "error" in res:
            return {"error": res["error"]}
        return {"status": "success", "message": f"Added {quantity} to cart."}

    def _prepare_checkout() -> dict:
        import hashlib
        import uuid
        from datetime import UTC, datetime, timedelta

        from app.core.config import get_settings
        from app.modules.commerce.cart_service import checkout_cart
        from app.modules.commerce.models import CheckoutSession

        idem_key = f"demo_chk_{uuid.uuid4().hex[:8]}"
        delivery_address = {"address_line": "Store pickup / Demo", "city": "Demo City"}
        res = checkout_cart(db, business_id, buyer_id, delivery_address, idem_key)
        if "error" in res:
            return {"error": res["error"]}

        order_id = res["order_id"]
        token = uuid.uuid4().hex
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        session = CheckoutSession(
            business_id=business_id,
            order_id=UUID(order_id),
            token_hash=token_hash,
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
        )
        db.add(session)
        db.flush()

        settings = get_settings()
        base_url = settings.public_artifact_base_url or "https://stockaware.vaaani.co.in"
        checkout_url = f"{base_url}/pay/{token}"

        return {
            "status": "success",
            "order_id": order_id,
            "checkout_url": checkout_url,
            "message": f"Checkout prepared. Share this URL with the customer: {checkout_url}",
        }

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
        StructuredTool.from_function(
            func=_get_store_info,
            name="get_store_info",
            description="Get information about the store (e.g. description, support number, policies).",
        ),
        StructuredTool.from_function(
            func=_get_product_variants,
            name="get_product_variants",
            description="Get available size/color variants for a product. Call this before add_to_cart if the product has variants.",
            args_schema=GetProductVariantsInput,
        ),
        StructuredTool.from_function(
            func=_add_to_cart,
            name="add_to_cart",
            description="Add a product (optionally a specific variant) to the cart with a specific quantity. Always confirm the item with the customer before calling this.",
            args_schema=AddToCartInput,
        ),
        StructuredTool.from_function(
            func=_prepare_checkout,
            name="prepare_checkout",
            description="Prepare checkout for the buyer's cart and return the checkout URL.",
        ),
    ]
