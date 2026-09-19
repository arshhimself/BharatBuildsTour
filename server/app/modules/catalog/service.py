from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.catalog import repository
from app.modules.catalog.models import Product
from app.modules.catalog.normalization import normalize_catalog_text
from app.modules.catalog.schemas import (
    CatalogCandidate,
    CatalogMatchIn,
    CatalogMatchOut,
    CatalogMatchStatus,
    MatchType,
    ProductOut,
    normalized_unit,
)


def get_products(
    session: Session,
    business_id: UUID,
    *,
    include_inactive: bool,
    limit: int,
    offset: int,
) -> list[ProductOut]:
    products = repository.list_products(
        session,
        business_id,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
    return [
        ProductOut(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            sellable_unit=product.sellable_unit,
            stock_unit=product.stock_unit,
            pack_size=product.pack_size,
            indivisible=product.indivisible,
            base_unit_price_paise=product.base_unit_price_paise,
            gst_rate_bps=product.gst_rate_bps,
            active=product.active,
        )
        for product in products
    ]


def get_product(session: Session, business_id: UUID, product_id: UUID) -> ProductOut | None:
    product = repository.get_active_product(session, business_id, product_id)
    return _product_out(product) if product is not None else None


def filter_products_by_price(
    session: Session,
    business_id: UUID,
    *,
    min_price_paise: int | None = None,
    max_price_paise: int | None = None,
    limit: int = 5,
) -> list[ProductOut]:
    if min_price_paise is not None and min_price_paise < 0:
        raise ValueError("min_price_paise must be non-negative")
    if max_price_paise is not None and max_price_paise < 0:
        raise ValueError("max_price_paise must be non-negative")
    if (
        min_price_paise is not None
        and max_price_paise is not None
        and min_price_paise > max_price_paise
    ):
        raise ValueError("minimum price cannot exceed maximum price")
    products = repository.filter_products_by_price(
        session,
        business_id,
        min_price_paise=min_price_paise,
        max_price_paise=max_price_paise,
        limit=max(1, min(limit, 20)),
    )
    return [_product_out(product) for product in products]


def list_categories(session: Session, business_id: UUID) -> list[dict[str, str]]:
    return [
        {"id": str(category.id), "name": category.name}
        for category in repository.list_categories(session, business_id)
    ]


def browse_category(
    session: Session, business_id: UUID, category_name: str, *, limit: int = 20
) -> tuple[dict[str, str] | None, list[ProductOut]]:
    normalized = " ".join(category_name.casefold().split())
    category = (
        repository.get_category_by_normalized_name(session, business_id, normalized)
        if normalized
        else None
    )
    if category is None:
        return None, []
    products = repository.list_products_in_category(
        session, business_id, category.id, limit=max(1, min(limit, 20))
    )
    return {"id": str(category.id), "name": category.name}, [
        _product_out(product) for product in products
    ]


def _product_out(product: Product) -> ProductOut:
    return ProductOut(
        product_id=product.id,
        sku=product.sku,
        name=product.name,
        sellable_unit=product.sellable_unit,
        stock_unit=product.stock_unit,
        pack_size=product.pack_size,
        indivisible=product.indivisible,
        base_unit_price_paise=product.base_unit_price_paise,
        gst_rate_bps=product.gst_rate_bps,
        active=product.active,
    )


def search_products(session: Session, business_id: UUID, query: str) -> list[ProductOut]:
    """
    Search for active products by loosely matching on SKU, name, or alias.
    """
    if not query.strip():
        return []
    products = repository.fuzzy_match_candidates(session, business_id, query)
    return [
        ProductOut(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            sellable_unit=product.sellable_unit,
            stock_unit=product.stock_unit,
            pack_size=product.pack_size,
            indivisible=product.indivisible,
            base_unit_price_paise=product.base_unit_price_paise,
            gst_rate_bps=product.gst_rate_bps,
            active=product.active,
        )
        for product in products
    ]


def match_product(session: Session, business_id: UUID, request: CatalogMatchIn) -> CatalogMatchOut:
    normalized_query = normalize_catalog_text(request.requested_text)
    if not normalized_query:
        return _result(request, CatalogMatchStatus.NOT_FOUND, "NO_MATCH", "No match found.", [])

    matches = repository.exact_match_candidates(session, business_id, normalized_query)
    candidates = [_candidate(product, match_type) for product, match_type in matches]
    if not matches:
        return _result(request, CatalogMatchStatus.NOT_FOUND, "NO_MATCH", "No match found.", [])
    if len(matches) > 1:
        return _result(
            request,
            CatalogMatchStatus.AMBIGUOUS,
            "MULTIPLE_MATCHES",
            "Multiple active products match this request.",
            candidates,
        )

    product, match_type = matches[0]
    if normalized_unit(request.requested_unit) != normalized_unit(product.sellable_unit):
        return _result(
            request,
            CatalogMatchStatus.AMBIGUOUS,
            "UNIT_MISMATCH",
            (
                f"Unit '{request.requested_unit}' does not match product sellable unit "
                f"'{product.sellable_unit}' and no conversion exists."
            ),
            candidates,
        )

    reason_by_type = {
        MatchType.SKU: ("EXACT_SKU_MATCH", "Exact SKU match."),
        MatchType.NAME: ("EXACT_NAME_MATCH", "Exact name match."),
        MatchType.ALIAS: ("EXACT_ALIAS_MATCH", "Exact alias match."),
    }
    reason_code, reason = reason_by_type[match_type]
    return CatalogMatchOut(
        status=CatalogMatchStatus.MATCHED,
        requested_text=request.requested_text,
        selected_product_id=product.id,
        selected_sku=product.sku,
        reason=reason,
        reason_code=reason_code,
        candidates=candidates,
    )


def _candidate(product: Product, match_type: MatchType) -> CatalogCandidate:
    return CatalogCandidate(
        product_id=product.id,
        sku=product.sku,
        name=product.name,
        sellable_unit=product.sellable_unit,
        stock_unit=product.stock_unit,
        pack_size=product.pack_size,
        match_type=match_type,
    )


def _result(
    request: CatalogMatchIn,
    status: CatalogMatchStatus,
    reason_code: str,
    reason: str,
    candidates: list[CatalogCandidate],
) -> CatalogMatchOut:
    return CatalogMatchOut(
        status=status,
        requested_text=request.requested_text,
        selected_product_id=None,
        selected_sku=None,
        reason=reason,
        reason_code=reason_code,
        candidates=candidates,
    )
