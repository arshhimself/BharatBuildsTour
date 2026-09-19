from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("business_id", "id", name="uq_products_business_id_id"),
        UniqueConstraint("business_id", "sku", name="uq_products_business_sku"),
        UniqueConstraint(
            "business_id", "normalized_sku", name="uq_products_business_normalized_sku"
        ),
        CheckConstraint("pack_size > 0", name="ck_products_pack_size_positive"),
        CheckConstraint("cost_unit_paise >= 0", name="ck_products_cost_nonnegative"),
        CheckConstraint("base_unit_price_paise > 0", name="ck_products_price_positive"),
        CheckConstraint("gst_rate_bps BETWEEN 0 AND 10000", name="ck_products_gst_rate"),
        Index("ix_products_business_normalized_name", "business_id", "normalized_name"),
        Index("ix_products_business_category", "business_id", "category_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="RESTRICT"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(80), nullable=False)
    normalized_sku: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sellable_unit: Mapped[str] = mapped_column(String(32), nullable=False)
    stock_unit: Mapped[str] = mapped_column(String(32), nullable=False)
    pack_size: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    indivisible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    cost_unit_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    base_unit_price_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    gst_rate_bps: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan"
    )
    media: Mapped[list["ProductMedia"]] = relationship(
        "ProductMedia", back_populates="product", cascade="all, delete-orphan"
    )

    @property
    def price_paise(self) -> int:
        return self.base_unit_price_paise

    @price_paise.setter
    def price_paise(self, value: int) -> None:
        self.base_unit_price_paise = value

    def __init__(self, **kw):
        if "price_paise" in kw and "base_unit_price_paise" not in kw:
            kw["base_unit_price_paise"] = kw.pop("price_paise")
        if "sku" in kw and "normalized_sku" not in kw and kw["sku"] is not None:
            from app.modules.catalog.normalization import normalize_catalog_text

            kw["normalized_sku"] = normalize_catalog_text(kw["sku"])
        if "name" in kw and "normalized_name" not in kw and kw["name"] is not None:
            from app.modules.catalog.normalization import normalize_catalog_text

            kw["normalized_name"] = normalize_catalog_text(kw["name"])
        kw.setdefault("sellable_unit", "pcs")
        kw.setdefault("stock_unit", "pcs")
        kw.setdefault("pack_size", Decimal("1.000"))
        kw.setdefault("cost_unit_paise", 0)
        kw.setdefault("gst_rate_bps", 0)
        super().__init__(**kw)


class ProductAlias(Base):
    __tablename__ = "product_aliases"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["products.business_id", "products.id"],
            ondelete="RESTRICT",
            name="fk_product_aliases_business_product",
        ),
        UniqueConstraint(
            "business_id",
            "normalized_alias",
            "product_id",
            name="uq_product_aliases_business_alias_product",
        ),
        Index("ix_product_aliases_business_product", "business_id", "product_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    alias_text: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(255), nullable=False)


class ProductSubstitute(Base):
    __tablename__ = "product_substitutes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["products.business_id", "products.id"],
            ondelete="RESTRICT",
            name="fk_product_substitutes_business_product",
        ),
        ForeignKeyConstraint(
            ["business_id", "substitute_product_id"],
            ["products.business_id", "products.id"],
            ondelete="RESTRICT",
            name="fk_product_substitutes_business_substitute",
        ),
        UniqueConstraint(
            "business_id",
            "product_id",
            "substitute_product_id",
            name="uq_product_substitutes_pair",
        ),
        CheckConstraint(
            "product_id <> substitute_product_id",
            name="ck_product_substitutes_not_self",
        ),
        CheckConstraint("rank > 0", name="ck_product_substitutes_rank_positive"),
        Index("ix_product_substitutes_business_product_rank", "business_id", "product_id", "rank"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    substitute_product_id: Mapped[UUID] = mapped_column(nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["products.business_id", "products.id"],
            ondelete="CASCADE",
            name="fk_product_variants_business_product",
        ),
        UniqueConstraint("business_id", "id", name="uq_product_variants_business_id_id"),
        UniqueConstraint("business_id", "sku", name="uq_product_variants_business_sku"),
        Index("ix_product_variants_business_product", "business_id", "product_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    sku: Mapped[str] = mapped_column(String(80), nullable=False)
    size: Mapped[str | None] = mapped_column(String(32))
    color: Mapped[str | None] = mapped_column(String(32))
    price_override_paise: Mapped[int | None] = mapped_column(BigInteger)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    product: Mapped[Product] = relationship("Product", back_populates="variants")


class ProductMedia(Base):
    __tablename__ = "product_media"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_id", "product_id"],
            ["products.business_id", "products.id"],
            ondelete="CASCADE",
            name="fk_product_media_business_product",
        ),
        UniqueConstraint("business_id", "id", name="uq_product_media_business_id_id"),
        Index("ix_product_media_business_product", "business_id", "product_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    media_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    media_type: Mapped[str] = mapped_column(String(32), nullable=False, server_default="image")
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    product: Mapped[Product] = relationship("Product", back_populates="media")
