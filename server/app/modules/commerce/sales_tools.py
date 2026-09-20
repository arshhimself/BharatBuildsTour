"""Tenant-bound catalog tools exposed only to the Number-B salesperson."""

from decimal import Decimal
from typing import Any
from uuid import UUID

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.catalog.models import Product, ProductMedia, ProductVariant
from app.modules.catalog.normalization import normalize_catalog_text
from app.modules.catalog.service import (
    browse_category,
    filter_products_by_price,
    get_product,
    get_products,
    list_categories,
    search_products,
)
from app.modules.identity.models import Business, StoreProfile
from app.modules.identity.owner_models import Category
from app.modules.inventory.models import Inventory
from app.modules.inventory.schemas import InventoryCheckIn
from app.modules.inventory.service import check_stock


class BrowseCatalogInput(BaseModel):
    limit: int = Field(default=5, ge=1, le=10)


class SearchProductsInput(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=120,
        description="Clean product terms only; never the full customer sentence.",
    )


class BrowseCategoryInput(BaseModel):
    category: str = Field(min_length=1, max_length=120)
    limit: int = Field(default=5, ge=1, le=10)


class GetProductInput(BaseModel):
    product_id: str = Field(description="Product UUID from trusted conversation state or a tool")


class CheckInventoryInput(BaseModel):
    product_id: str
    requested_qty: float = Field(default=1, gt=0)


class CheckVariantInput(BaseModel):
    product_id: str
    size: str | None = Field(default=None, max_length=32)
    color: str | None = Field(default=None, max_length=32)


class FilterProductsInput(BaseModel):
    min_price_paise: int | None = Field(default=None, ge=0)
    max_price_paise: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, max_length=120)
    keywords: str | None = Field(default=None, max_length=120)
    limit: int = Field(default=5, ge=1, le=10)


class SimilarProductsInput(BaseModel):
    product_id: str
    cheaper_only: bool = False
    limit: int = Field(default=5, ge=1, le=10)


class EmptyInput(BaseModel):
    pass


def _uuid(value: Any) -> UUID | None:
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        try:
            return UUID(value)
        except (TypeError, ValueError):
            return None
    return None


def _quantity(value: Decimal | int | float | str | None) -> str | None:
    if value is None:
        return None
    try:
        d = Decimal(str(value))
        if d == d.to_integral_value():
            return str(int(d))
        return str(d.normalize())
    except Exception:
        return str(value)


def _product_fact(db: Session, business_id: UUID, product_id: UUID) -> dict:
    product = db.scalar(
        select(Product).where(
            Product.business_id == business_id,
            Product.id == product_id,
            Product.active.is_(True),
        )
    )
    if product is None:
        return {"error": "Product not found"}
    category = None
    if product.category_id:
        category = db.scalar(
            select(Category).where(
                Category.business_id == business_id,
                Category.id == product.category_id,
            )
        )
    media = list(
        db.scalars(
            select(ProductMedia)
            .where(
                ProductMedia.business_id == business_id,
                ProductMedia.product_id == product.id,
                ProductMedia.media_type == "image",
            )
            .order_by(ProductMedia.position, ProductMedia.id)
        ).all()
    )
    inventory = db.scalar(
        select(Inventory).where(
            Inventory.business_id == business_id,
            Inventory.product_id == product.id,
            Inventory.variant_id.is_(None),
        )
    )
    if inventory is None:
        inventory = db.scalar(
            select(Inventory).where(
                Inventory.business_id == business_id,
                Inventory.product_id == product.id,
            )
        )
    variant_inv_map = {
        inv.variant_id: inv.on_hand_qty
        for inv in db.scalars(
            select(Inventory).where(
                Inventory.business_id == business_id,
                Inventory.product_id == product.id,
                Inventory.variant_id.is_not(None),
            )
        ).all()
    }
    variants = list(
        db.scalars(
            select(ProductVariant)
            .where(
                ProductVariant.business_id == business_id,
                ProductVariant.product_id == product.id,
                ProductVariant.active.is_(True),
            )
            .order_by(ProductVariant.size, ProductVariant.color, ProductVariant.sku)
        ).all()
    )
    available_qty = inventory.on_hand_qty if inventory else None
    variant_facts = []
    for variant in variants:
        v_qty = variant_inv_map.get(variant.id)
        if v_qty is not None:
            is_avail = v_qty > 0
        else:
            is_avail = available_qty is not None and available_qty > 0
        variant_facts.append(
            {
                "id": str(variant.id),
                "sku": variant.sku,
                "size": variant.size,
                "color": variant.color,
                "price_paise": variant.price_override_paise
                if variant.price_override_paise is not None
                else product.base_unit_price_paise,
                "available": is_avail,
            }
        )
    return {
        "id": str(product.id),
        "name": product.name,
        "sku": product.sku,
        "category_id": str(category.id) if category else None,
        "category": category.name if category else None,
        "sellable_unit": product.sellable_unit,
        "stock_unit": product.stock_unit,
        "price_paise": product.base_unit_price_paise,
        "gst_rate_bps": product.gst_rate_bps,
        "available_qty": _quantity(available_qty),
        "primary_media_url": media[0].media_url if media else None,
        "media_urls": [item.media_url for item in media],
        "variants": variant_facts,
    }


def product_facts(
    db: Session, business_id: UUID, product_ids: list[str], *, limit: int = 10
) -> list[dict]:
    facts: list[dict] = []
    for raw_id in product_ids[:limit]:
        parsed = _uuid(raw_id)
        if parsed is None:
            continue
        fact = _product_fact(db, business_id, parsed)
        if "error" not in fact:
            facts.append(fact)
    return facts


def _store_info(db: Session, business_id: UUID) -> dict:
    business = db.scalar(select(Business).where(Business.id == business_id))
    profile = db.scalar(select(StoreProfile).where(StoreProfile.business_id == business_id))
    if business is None:
        return {"error": "Store not found"}
    return {
        "name": business.display_name,
        "description": profile.description if profile else None,
        "store_type": profile.store_type if profile else None,
        "address_line": profile.address_line if profile else business.billing_address,
        "city": profile.city if profile else None,
        "support_number": profile.support_number if profile else None,
        "opening_hours": profile.opening_hours if profile else None,
        "delivery_info": profile.delivery_info if profile else None,
        "return_policy": profile.return_policy if profile else None,
    }


def build_customer_sales_tools(
    db: Session,
    business_id: UUID,
    *,
    buyer_id: UUID | None = None,
    message_id: str = "commerce-turn",
    context: dict | None = None,
) -> list[StructuredTool]:
    """Build safe domain tools with tenant and buyer authority closed over."""

    def _browse(limit: int = 5) -> list[dict]:
        rows = get_products(db, business_id, include_inactive=False, limit=limit, offset=0)
        return product_facts(db, business_id, [str(row.product_id) for row in rows], limit=limit)

    def _search(query: str) -> list[dict]:
        rows = search_products(db, business_id, query)
        return product_facts(db, business_id, [str(row.product_id) for row in rows])

    def _categories() -> list[dict]:
        results: list[dict] = []
        for category in list_categories(db, business_id):
            product = db.scalar(
                select(Product)
                .where(
                    Product.business_id == business_id,
                    Product.category_id == category.id,
                    Product.active.is_(True),
                )
                .order_by(Product.sku, Product.id)
            )
            media_url = None
            if product:
                media_url = db.scalar(
                    select(ProductMedia.media_url)
                    .where(
                        ProductMedia.business_id == business_id,
                        ProductMedia.product_id == product.id,
                        ProductMedia.media_type == "image",
                    )
                    .order_by(ProductMedia.position, ProductMedia.id)
                )
            count = db.scalar(
                select(func.count(Product.id)).where(
                    Product.business_id == business_id,
                    Product.category_id == category.id,
                    Product.active.is_(True),
                )
            )
            results.append(
                {
                    "id": str(category.id),
                    "name": category.name,
                    "product_count": count or 0,
                    "representative_media_url": media_url,
                }
            )
        return results

    def _browse_category(category: str, limit: int = 5) -> dict:
        resolved, rows = browse_category(db, business_id, category, limit=limit)
        if resolved is None:
            return {"error": "Category not found", "products": []}
        return {
            "category_id": str(resolved.id),
            "category": resolved.name,
            "products": product_facts(
                db, business_id, [str(row.product_id) for row in rows], limit=limit
            ),
        }

    def _get(product_id: str) -> dict:
        parsed = _uuid(product_id)
        if parsed is None or get_product(db, business_id, parsed) is None:
            return {"error": "Product not found"}
        return _product_fact(db, business_id, parsed)

    def _variants(product_id: str) -> dict:
        product = _get(product_id)
        if "error" in product:
            return product
        return {"product_id": product_id, "product": product, "variants": product["variants"]}

    def _inventory(product_id: str, requested_qty: float = 1) -> dict:
        parsed = _uuid(product_id)
        if parsed is None or get_product(db, business_id, parsed) is None:
            return {"error": "Product not found"}
        try:
            result = check_stock(
                db,
                business_id,
                InventoryCheckIn(
                    business_id=business_id,
                    run_id="customer-commerce",
                    product_id=parsed,
                    requested_qty=str(requested_qty),
                ),
            )
        except Exception:
            return {"error": "Inventory unavailable"}
        return {
            "product_id": str(result.product_id),
            "status": result.status.value,
            "available_qty": str(result.available_qty),
            "stock_unit": result.stock_unit,
        }

    def _variant_inventory(
        product_id: str, size: str | None = None, color: str | None = None
    ) -> dict:
        product = _get(product_id)
        if "error" in product:
            return product
        size_key = normalize_catalog_text(size or "")
        color_key = normalize_catalog_text(color or "")
        matches = [
            variant
            for variant in product["variants"]
            if (not size_key or normalize_catalog_text(variant.get("size") or "") == size_key)
            and (not color_key or normalize_catalog_text(variant.get("color") or "") == color_key)
        ]
        return {"product": product, "variants": matches}

    def _filter(
        min_price_paise: int | None = None,
        max_price_paise: int | None = None,
        category: str | None = None,
        keywords: str | None = None,
        limit: int = 5,
    ) -> list[dict]:
        rows = filter_products_by_price(
            db,
            business_id,
            min_price_paise=min_price_paise,
            max_price_paise=max_price_paise,
            limit=20,
        )
        facts = product_facts(db, business_id, [str(row.product_id) for row in rows], limit=20)
        if category:
            category_key = normalize_catalog_text(category)
            facts = [
                fact
                for fact in facts
                if normalize_catalog_text(fact.get("category") or "") == category_key
            ]
        if keywords:
            tokens = set(normalize_catalog_text(keywords).split())
            facts = [
                fact for fact in facts if tokens & set(normalize_catalog_text(fact["name"]).split())
            ]
        return facts[:limit]

    def _similar(product_id: str, cheaper_only: bool = False, limit: int = 5) -> list[dict]:
        parsed = _uuid(product_id)
        source = _product_fact(db, business_id, parsed) if parsed else {"error": "invalid"}
        if "error" in source:
            return []
        statement = select(Product).where(
            Product.business_id == business_id,
            Product.active.is_(True),
            Product.id != parsed,
        )
        if source.get("category_id"):
            statement = statement.where(Product.category_id == UUID(source["category_id"]))
        if cheaper_only:
            statement = statement.where(Product.base_unit_price_paise < source["price_paise"])
        rows = list(
            db.scalars(
                statement.order_by(Product.base_unit_price_paise.desc(), Product.sku).limit(limit)
            ).all()
        )
        return product_facts(db, business_id, [str(row.id) for row in rows], limit=limit)

    tools = [
        StructuredTool.from_function(
            _browse,
            name="browse_catalog",
            description="Show real active products for a broad browse request.",
            args_schema=BrowseCatalogInput,
        ),
        StructuredTool.from_function(
            _search,
            name="search_products",
            description="Search real products using clean product terms only.",
            args_schema=SearchProductsInput,
        ),
        StructuredTool.from_function(
            _categories,
            name="list_categories",
            description="List real store categories.",
            args_schema=EmptyInput,
        ),
        StructuredTool.from_function(
            _browse_category,
            name="browse_category",
            description="Resolve a real category and show its products.",
            args_schema=BrowseCategoryInput,
        ),
        StructuredTool.from_function(
            _get,
            name="get_product",
            description="Fetch authoritative details for one tenant product UUID.",
            args_schema=GetProductInput,
        ),
        StructuredTool.from_function(
            _variants,
            name="get_product_variants",
            description="List real active sizes and colors for a selected product.",
            args_schema=GetProductInput,
        ),
        StructuredTool.from_function(
            _inventory,
            name="check_inventory",
            description="Check authoritative on-hand inventory for a product.",
            args_schema=CheckInventoryInput,
        ),
        StructuredTool.from_function(
            _variant_inventory,
            name="check_variant_inventory",
            description="Check whether a selected product has an active size/color variant backed by product on-hand stock.",
            args_schema=CheckVariantInput,
        ),
        StructuredTool.from_function(
            _filter,
            name="filter_products_by_price",
            description="Find real products within price/category/keyword constraints.",
            args_schema=FilterProductsInput,
        ),
        StructuredTool.from_function(
            _similar,
            name="find_similar_products",
            description="Find deterministic alternatives from the selected product's real category, optionally cheaper.",
            args_schema=SimilarProductsInput,
        ),
        StructuredTool.from_function(
            lambda: _store_info(db, business_id),
            name="get_store_info",
            description="Fetch authoritative store information and policies.",
            args_schema=EmptyInput,
        ),
    ]
    if buyer_id is not None:
        from app.modules.commerce.cart_tools import build_cart_tools

        tools.extend(build_cart_tools(db, business_id, buyer_id, message_id, context=context))
    return tools
