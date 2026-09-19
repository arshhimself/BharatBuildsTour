from collections import defaultdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.catalog.models import Product, ProductAlias
from app.modules.catalog.schemas import MatchType
from app.modules.identity.owner_models import Category


def list_products(
    session: Session,
    business_id: UUID,
    *,
    include_inactive: bool,
    limit: int,
    offset: int,
) -> list[Product]:
    statement = select(Product).where(Product.business_id == business_id)
    if not include_inactive:
        statement = statement.where(Product.active.is_(True))
    statement = statement.order_by(Product.sku, Product.id).limit(limit).offset(offset)
    return list(session.scalars(statement).all())


def get_active_product(session: Session, business_id: UUID, product_id: UUID) -> Product | None:
    return session.scalar(
        select(Product).where(
            Product.business_id == business_id,
            Product.id == product_id,
            Product.active.is_(True),
        )
    )


def filter_products_by_price(
    session: Session,
    business_id: UUID,
    *,
    min_price_paise: int | None,
    max_price_paise: int | None,
    limit: int,
) -> list[Product]:
    statement = select(Product).where(
        Product.business_id == business_id,
        Product.active.is_(True),
    )
    if min_price_paise is not None:
        statement = statement.where(Product.base_unit_price_paise >= min_price_paise)
    if max_price_paise is not None:
        statement = statement.where(Product.base_unit_price_paise <= max_price_paise)
    statement = statement.order_by(
        Product.base_unit_price_paise,
        Product.sku,
        Product.id,
    ).limit(limit)
    return list(session.scalars(statement).all())


def list_categories(session: Session, business_id: UUID) -> list[Category]:
    """Return only categories owned by this tenant, in stable display order."""
    return list(
        session.scalars(
            select(Category)
            .where(Category.business_id == business_id)
            .order_by(Category.name, Category.id)
        ).all()
    )


def get_category_by_normalized_name(
    session: Session, business_id: UUID, normalized_name: str
) -> Category | None:
    # Categories predate a normalized-name column, so this needs no migration.
    for category in list_categories(session, business_id):
        if " ".join(category.name.casefold().split()) == normalized_name:
            return category
    return None


def list_products_in_category(
    session: Session, business_id: UUID, category_id: UUID, *, limit: int
) -> list[Product]:
    return list(
        session.scalars(
            select(Product)
            .where(
                Product.business_id == business_id,
                Product.category_id == category_id,
                Product.active.is_(True),
            )
            .order_by(Product.sku, Product.id)
            .limit(limit)
        ).all()
    )


def exact_match_candidates(
    session: Session, business_id: UUID, normalized_query: str
) -> list[tuple[Product, MatchType]]:
    direct_statement = select(Product).where(
        Product.business_id == business_id,
        Product.active.is_(True),
        (Product.normalized_sku == normalized_query)
        | (Product.normalized_name == normalized_query),
    )
    direct_products = list(session.scalars(direct_statement).all())

    alias_statement = (
        select(Product)
        .join(
            ProductAlias,
            (ProductAlias.business_id == Product.business_id)
            & (ProductAlias.product_id == Product.id),
        )
        .where(
            Product.business_id == business_id,
            ProductAlias.business_id == business_id,
            Product.active.is_(True),
            ProductAlias.normalized_alias == normalized_query,
        )
    )
    alias_products = list(session.scalars(alias_statement).all())

    sources: dict[UUID, set[MatchType]] = defaultdict(set)
    products: dict[UUID, Product] = {}
    for product in direct_products:
        products[product.id] = product
        if product.normalized_sku == normalized_query:
            sources[product.id].add(MatchType.SKU)
        if product.normalized_name == normalized_query:
            sources[product.id].add(MatchType.NAME)
    for product in alias_products:
        products[product.id] = product
        sources[product.id].add(MatchType.ALIAS)

    priority = (MatchType.SKU, MatchType.NAME, MatchType.ALIAS)
    result = [
        (product, next(match_type for match_type in priority if match_type in sources[product_id]))
        for product_id, product in products.items()
    ]
    return sorted(result, key=lambda item: (item[0].sku, str(item[0].id)))


def fuzzy_match_candidates(session: Session, business_id: UUID, query: str) -> list[Product]:
    """
    Find active products by loosely matching on SKU, name, or alias.
    Uses ILIKE on a wildcard-wrapped query for the demo.
    """
    wildcard_query = (
        f"%{query.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')}%"
    )

    direct_statement = select(Product).where(
        Product.business_id == business_id,
        Product.active.is_(True),
        (Product.sku.ilike(wildcard_query, escape="\\"))
        | (Product.name.ilike(wildcard_query, escape="\\")),
    )
    direct_products = list(
        session.scalars(direct_statement.order_by(Product.sku, Product.id).limit(20)).all()
    )

    alias_statement = (
        select(Product)
        .join(
            ProductAlias,
            (ProductAlias.business_id == Product.business_id)
            & (ProductAlias.product_id == Product.id),
        )
        .where(
            Product.business_id == business_id,
            ProductAlias.business_id == business_id,
            Product.active.is_(True),
            ProductAlias.alias_text.ilike(wildcard_query, escape="\\"),
        )
    )
    alias_products = list(
        session.scalars(alias_statement.order_by(Product.sku, Product.id).limit(20)).all()
    )

    products_by_id = {p.id: p for p in direct_products + alias_products}
    return sorted(products_by_id.values(), key=lambda p: (p.sku, str(p.id)))[:20]
