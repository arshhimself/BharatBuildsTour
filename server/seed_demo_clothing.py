import os
import sys
from decimal import Decimal
from uuid import uuid4

# Setup paths
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
sys.path.append(os.path.dirname(__file__))

from app.db.session import transaction_session
from app.modules.catalog.models import Product, ProductMedia
from app.modules.identity.models import Business, StoreProfile
from app.modules.identity.owner_models import Category

# Seed images (public unspalsh or placeholder image links for demo)
IMAGES = {
    "tshirt_black": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800&q=80",
    "tshirt_white": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&q=80",
    "chinos_navy": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&q=80",
    "hoodie_grey": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800&q=80",
    "jeans_blue": "https://images.unsplash.com/photo-1542272604-780c8d4513a8?w=800&q=80",
}


def seed_data():
    with transaction_session() as db:
        business = db.query(Business).first()
        if not business:
            business = Business(id=uuid4(), display_name="Rehbar Clothing", gstin="27AADCB2230M1Z2")
            db.add(business)
            db.flush()

        business.display_name = "Rehbar Clothing"

        # Get or create StoreProfile
        store_profile = (
            db.query(StoreProfile).filter(StoreProfile.business_id == business.id).first()
        )
        if not store_profile:
            store_profile = StoreProfile(
                business_id=business.id,
                display_name="Rehbar Clothing",
                description="Premium quality t-shirts, jeans, and hoodies at affordable prices.",
                store_type="Retail Clothing",
                city="Mumbai",
                support_number="+91 99999 00000",
                opening_hours="10 AM - 9 PM, All Days",
                delivery_info="Standard delivery 3-5 days. Same day delivery available in Mumbai.",
                return_policy="7-day no questions asked return policy.",
            )
            db.add(store_profile)
        else:
            store_profile.display_name = "Rehbar Clothing"
            store_profile.description = (
                "Premium quality t-shirts, jeans, and hoodies at affordable prices."
            )

        # Clear existing catalog data for demo
        from app.modules.catalog.models import ProductAlias, ProductSubstitute
        from app.modules.inventory.models import Inventory

        db.query(Inventory).delete()
        db.query(ProductAlias).delete()
        db.query(ProductSubstitute).delete()
        db.query(ProductMedia).delete()
        db.query(Product).delete()
        db.query(Category).delete()

        db.flush()

        # Create Categories
        cat_tshirts = Category(business_id=business.id, name="T-Shirts")
        cat_bottoms = Category(business_id=business.id, name="Bottoms")
        cat_winter = Category(business_id=business.id, name="Winter Wear")

        db.add_all([cat_tshirts, cat_bottoms, cat_winter])
        db.flush()

        # Create Products
        products_data = [
            {
                "sku": "TSH-BLK-01",
                "name": "Premium Cotton Black T-Shirt",
                "cat": cat_tshirts.id,
                "price": 599,
                "image": IMAGES["tshirt_black"],
            },
            {
                "sku": "TSH-WHT-01",
                "name": "Classic White Crew Neck T-Shirt",
                "cat": cat_tshirts.id,
                "price": 499,
                "image": IMAGES["tshirt_white"],
            },
            {
                "sku": "CHN-NVY-01",
                "name": "Navy Blue Slim Fit Chinos",
                "cat": cat_bottoms.id,
                "price": 1299,
                "image": IMAGES["chinos_navy"],
            },
            {
                "sku": "JNS-BLU-01",
                "name": "Classic Blue Denim Jeans",
                "cat": cat_bottoms.id,
                "price": 1499,
                "image": IMAGES["jeans_blue"],
            },
            {
                "sku": "HD-GRY-01",
                "name": "Grey Pullover Hoodie",
                "cat": cat_winter.id,
                "price": 1199,
                "image": IMAGES["hoodie_grey"],
            },
        ]

        for p_data in products_data:
            product = Product(
                business_id=business.id,
                sku=p_data["sku"],
                normalized_sku=p_data["sku"].lower(),
                name=p_data["name"],
                normalized_name=p_data["name"].lower(),
                sellable_unit="piece",
                stock_unit="piece",
                pack_size=Decimal("1"),
                indivisible=True,
                cost_unit_paise=p_data["price"] * 100 // 2,
                base_unit_price_paise=p_data["price"] * 100,
                gst_rate_bps=1200,
                active=True,
                category_id=p_data["cat"],
            )
            db.add(product)
            db.flush()

            media = ProductMedia(
                business_id=business.id,
                product_id=product.id,
                media_type="image",
                url=p_data["image"],
                sort_order=0,
                alt_text=p_data["name"],
                active=True,
            )
            db.add(media)

            # Add ProductVariants
            from app.modules.catalog.models import ProductVariant

            sizes = ["S", "M", "L", "XL"]
            for size in sizes:
                variant = ProductVariant(
                    business_id=business.id,
                    product_id=product.id,
                    sku=f"{p_data['sku']}-{size}",
                    size=size,
                    active=True,
                )
                db.add(variant)

            # Also add to inventory at the Product level (as per current schema constraints)
            from app.modules.inventory.models import Inventory

            inv = Inventory(
                business_id=business.id,
                product_id=product.id,
                on_hand_qty=Decimal("100"),
                reorder_threshold=Decimal("10"),
            )
            db.add(inv)

        print("Demo clothing catalog seeded successfully!")


if __name__ == "__main__":
    seed_data()
