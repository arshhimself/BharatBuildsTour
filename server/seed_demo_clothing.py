"""Idempotent clothing catalog & store profile seed for Rehbar Clothing demo business.

Run with: python seed_demo_clothing.py
"""

from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import transaction_session
from app.modules.catalog.models import Product, ProductAlias, ProductMedia, ProductVariant
from app.modules.catalog.normalization import normalize_catalog_text
from app.modules.identity.models import StoreProfile
from app.modules.identity.owner_models import Category
from app.modules.inventory.models import Inventory
from app.seed import DEMO_BUSINESS_ID

CLOTHING_CATEGORIES = [
    "T-Shirts",
    "Shirts",
    "Hoodies & Sweatshirts",
    "Denim & Trousers",
    "Jackets & Coats",
    "Accessories",
]

CLOTHING_PRODUCTS = [
    {
        "sku": "CLOTH-TSHIRT-BLK",
        "name": "Oversized Black T-Shirt",
        "category": "T-Shirts",
        "price_paise": 129900,
        "cost_paise": 50000,
        "media": ["https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["black t shirt", "black tshirt", "oversized tshirt", "black tee"],
    },
    {
        "sku": "CLOTH-TSHIRT-WHT",
        "name": "Classic White Crew Tee",
        "category": "T-Shirts",
        "price_paise": 99900,
        "cost_paise": 40000,
        "media": ["https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["white tee", "white tshirt", "crew neck white"],
    },
    {
        "sku": "CLOTH-HOODIE-GRY",
        "name": "Heavyweight Grey Pullover Hoodie",
        "category": "Hoodies & Sweatshirts",
        "price_paise": 249900,
        "cost_paise": 110000,
        "media": ["https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800"],
        "sizes": ["M", "L", "XL"],
        "aliases": ["grey hoodie", "pullover hoodie", "grey sweatshirt"],
    },
    {
        "sku": "CLOTH-HOODIE-BLK",
        "name": "Signature Black Zip Hoodie",
        "category": "Hoodies & Sweatshirts",
        "price_paise": 279900,
        "cost_paise": 120000,
        "media": ["https://images.unsplash.com/photo-1509967419530-da38b4704bc6?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["black hoodie", "zip hoodie"],
    },
    {
        "sku": "CLOTH-DENIM-BLU",
        "name": "Vintage Wash Blue Denim Jacket",
        "category": "Jackets & Coats",
        "price_paise": 349900,
        "cost_paise": 160000,
        "media": ["https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["denim jacket", "blue denim", "jeans jacket"],
    },
    {
        "sku": "CLOTH-SHIRT-NVY",
        "name": "Navy Blue Linen Casual Shirt",
        "category": "Shirts",
        "price_paise": 189900,
        "cost_paise": 80000,
        "media": ["https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["navy shirt", "linen shirt", "blue casual shirt"],
    },
    {
        "sku": "CLOTH-CARGO-GRN",
        "name": "Tactical Olive Green Cargo Pants",
        "category": "Denim & Trousers",
        "price_paise": 229900,
        "cost_paise": 95000,
        "media": ["https://images.unsplash.com/photo-1517445312882-bc9910d016b7?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["cargo pants", "olive cargos", "green cargos"],
    },
    {
        "sku": "CLOTH-JOGGER-BLK",
        "name": "Slim Fit Black Joggers",
        "category": "Denim & Trousers",
        "price_paise": 169900,
        "cost_paise": 70000,
        "media": ["https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["black joggers", "trackpants", "sweatpants"],
    },
    {
        "sku": "CLOTH-POLO-RED",
        "name": "Pique Cotton Maroon Polo Shirt",
        "category": "T-Shirts",
        "price_paise": 139900,
        "cost_paise": 55000,
        "media": ["https://images.unsplash.com/photo-1625910513413-562624f1c1f2?w=800"],
        "sizes": ["M", "L", "XL"],
        "aliases": ["maroon polo", "red polo shirt", "pique polo"],
    },
    {
        "sku": "CLOTH-SWEATER-BEI",
        "name": "Beige Knitted Cable Sweater",
        "category": "Hoodies & Sweatshirts",
        "price_paise": 219900,
        "cost_paise": 90000,
        "media": ["https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800"],
        "sizes": ["M", "L", "XL"],
        "aliases": ["beige sweater", "knitted sweater", "cream sweater"],
    },
    {
        "sku": "CLOTH-CHINO-BEI",
        "name": "Stretch Khaki Chino Trousers",
        "category": "Denim & Trousers",
        "price_paise": 199900,
        "cost_paise": 85000,
        "media": ["https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["khaki chinos", "beige pants", "chinos"],
    },
    {
        "sku": "CLOTH-SHORTS-BLK",
        "name": "Athletic Sweat Shorts - Black",
        "category": "Denim & Trousers",
        "price_paise": 119900,
        "cost_paise": 45000,
        "media": ["https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["black shorts", "gym shorts", "sweat shorts"],
    },
    {
        "sku": "CLOTH-JACKET-BLK",
        "name": "Faux Leather Biker Jacket",
        "category": "Jackets & Coats",
        "price_paise": 429900,
        "cost_paise": 200000,
        "media": ["https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800"],
        "sizes": ["M", "L", "XL"],
        "aliases": ["leather jacket", "biker jacket", "black jacket"],
    },
    {
        "sku": "CLOTH-TSHIRT-GRN",
        "name": "Graphic Printed Sage Green Tee",
        "category": "T-Shirts",
        "price_paise": 119900,
        "cost_paise": 48000,
        "media": ["https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["green tshirt", "sage tee", "graphic tee"],
    },
    {
        "sku": "CLOTH-SHIRT-WHT",
        "name": "Mandarin Collar White Cotton Shirt",
        "category": "Shirts",
        "price_paise": 179900,
        "cost_paise": 75000,
        "media": ["https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["white shirt", "mandarin collar", "kurta shirt"],
    },
    {
        "sku": "CLOTH-VEST-BLK",
        "name": "Puffer Gilet Bodywarmer Vest",
        "category": "Jackets & Coats",
        "price_paise": 259900,
        "cost_paise": 110000,
        "media": ["https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=800"],
        "sizes": ["M", "L", "XL"],
        "aliases": ["puffer vest", "gilet", "sleeveless jacket"],
    },
    {
        "sku": "CLOTH-OVERCOAT-BRN",
        "name": "Wool Blend Camel Overcoat",
        "category": "Jackets & Coats",
        "price_paise": 599900,
        "cost_paise": 280000,
        "media": ["https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800"],
        "sizes": ["M", "L", "XL"],
        "aliases": ["trench coat", "overcoat", "camel coat", "long coat"],
    },
    {
        "sku": "CLOTH-TRACKSUIT-NVY",
        "name": "Navy Blue Two-Piece Tracksuit",
        "category": "Hoodies & Sweatshirts",
        "price_paise": 329900,
        "cost_paise": 140000,
        "media": ["https://images.unsplash.com/photo-1483721074892-4a85df90a887?w=800"],
        "sizes": ["S", "M", "L", "XL"],
        "aliases": ["tracksuit", "navy tracksuit", "matching set"],
    },
    {
        "sku": "CLOTH-CAP-BLK",
        "name": "Embroidered Streetwear Baseball Cap",
        "category": "Accessories",
        "price_paise": 79900,
        "cost_paise": 25000,
        "media": ["https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=800"],
        "sizes": ["Free Size"],
        "aliases": ["black cap", "baseball hat", "streetwear cap"],
    },
    {
        "sku": "CLOTH-BEANIE-GRY",
        "name": "Ribbed Knit Grey Winter Beanie",
        "category": "Accessories",
        "price_paise": 59900,
        "cost_paise": 18000,
        "media": ["https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=800"],
        "sizes": ["Free Size"],
        "aliases": ["beanie", "winter cap", "grey beanie"],
    },
]


CLOTHING_CATEGORIES = [
    "T-Shirts",
    "Hoodies & Sweatshirts",
    "Jackets & Coats",
    "Shirts",
    "Denim & Trousers",
    "Accessories",
]


def seed_clothing_catalog(session: Session, business_id: UUID) -> None:
    """Seed or update Rehbar Clothing demo catalog with products, variants, media, and store profile."""

    # 1. Categories
    categories: dict[str, Category] = {}
    for cat_name in CLOTHING_CATEGORIES:
        cat_id = uuid5(NAMESPACE_URL, f"stockaware/clothing/category/{cat_name}")
        category = session.scalar(
            select(Category).where(Category.business_id == business_id, Category.name == cat_name)
        )
        if category is None:
            category = Category(id=cat_id, business_id=business_id, name=cat_name)
            session.add(category)
            session.flush()
        categories[cat_name] = category

    # 2. Store Profile
    profile = session.scalar(select(StoreProfile).where(StoreProfile.business_id == business_id))
    if profile is None:
        session.add(
            StoreProfile(
                business_id=business_id,
                description="Rehbar Clothing — Premium urban streetwear, oversized tees, hoodies, and denim.",
                store_type="Apparel & Fashion",
                address_line="102 Connaught Place, Inner Circle",
                city="New Delhi",
                support_number="+919876543210",
                opening_hours="10:00 AM - 9:00 PM (Mon-Sat)",
                delivery_info="Free Express Shipping across India on orders above ₹999. Delivered in 2-4 days.",
                return_policy="7 days hassle-free returns and exchanges.",
            )
        )

    # 3. Products, Variants, Inventory, Media
    for item in CLOTHING_PRODUCTS:
        product_id = uuid5(NAMESPACE_URL, f"stockaware/clothing/product/{item['sku']}")
        cat_obj = categories.get(item.get("category", "T-Shirts"))

        product = session.scalar(
            select(Product).where(Product.business_id == business_id, Product.sku == item["sku"])
        )
        if product is None:
            product = Product(
                id=product_id,
                business_id=business_id,
                sku=item["sku"],
                normalized_sku=normalize_catalog_text(item["sku"]),
                name=item["name"],
                normalized_name=normalize_catalog_text(item["name"]),
                category_id=cat_obj.id if cat_obj else None,
                sellable_unit="pcs",
                stock_unit="pcs",
                pack_size=Decimal("1.000"),
                cost_unit_paise=item["cost_paise"],
                base_unit_price_paise=item["price_paise"],
                gst_rate_bps=1200,  # 12% GST on apparel
            )
            session.add(product)
            session.flush()
        elif cat_obj and product.category_id != cat_obj.id:
            product.category_id = cat_obj.id
        session.flush()

        # Primary Inventory on Product
        inv = session.scalar(
            select(Inventory).where(
                Inventory.business_id == business_id, Inventory.product_id == product.id
            )
        )
        if inv is None:
            session.add(
                Inventory(
                    business_id=business_id,
                    product_id=product.id,
                    on_hand_qty=Decimal("50.000"),
                    reorder_threshold=Decimal("10.000"),
                )
            )

        # Product Media
        for pos, media_url in enumerate(item.get("media", []), start=1):
            media_id = uuid5(NAMESPACE_URL, f"stockaware/clothing/media/{item['sku']}/{pos}")
            existing_media = session.scalar(
                select(ProductMedia).where(
                    ProductMedia.business_id == business_id, ProductMedia.id == media_id
                )
            )
            if existing_media is None:
                session.add(
                    ProductMedia(
                        id=media_id,
                        business_id=business_id,
                        product_id=product.id,
                        media_url=media_url,
                        position=pos,
                    )
                )

        # Product Variants (Sizes)
        for size in item.get("sizes", []):
            var_sku = f"{item['sku']}-{size}"
            variant_id = uuid5(NAMESPACE_URL, f"stockaware/clothing/variant/{var_sku}")
            variant = session.scalar(
                select(ProductVariant).where(
                    ProductVariant.business_id == business_id, ProductVariant.sku == var_sku
                )
            )
            if variant is None:
                session.add(
                    ProductVariant(
                        id=variant_id,
                        business_id=business_id,
                        product_id=product.id,
                        sku=var_sku,
                        size=size,
                        active=True,
                    )
                )

        # Aliases
        for alias_text in item.get("aliases", []):
            normalized = normalize_catalog_text(alias_text)
            alias_id = uuid5(NAMESPACE_URL, f"stockaware/clothing/alias/{item['sku']}/{normalized}")
            alias = session.scalar(
                select(ProductAlias).where(
                    ProductAlias.business_id == business_id,
                    ProductAlias.normalized_alias == normalized,
                    ProductAlias.product_id == product.id,
                )
            )
            if alias is None:
                session.add(
                    ProductAlias(
                        id=alias_id,
                        business_id=business_id,
                        product_id=product.id,
                        alias_text=alias_text,
                        normalized_alias=normalized,
                    )
                )

    session.flush()


def main() -> None:
    with transaction_session() as session:
        seed_clothing_catalog(session, DEMO_BUSINESS_ID)
    print(f"Successfully seeded clothing catalog for business {DEMO_BUSINESS_ID}")


if __name__ == "__main__":
    main()
