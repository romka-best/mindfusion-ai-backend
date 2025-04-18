from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter, Query

from bot.database.main import firebase
from bot.database.models.common import Quota
from bot.database.models.product import Product, ProductCategory, ProductType


async def get_product(product_id: str) -> Optional[Product]:
    product_ref = firebase.db.collection(Product.COLLECTION_NAME).document(
        str(product_id)
    )
    product = await product_ref.get()

    if product.exists:
        return Product(**product.to_dict())


async def get_product_by_quota(
    quota: Quota,
) -> Optional[Product]:
    product_stream = (
        firebase.db.collection(Product.COLLECTION_NAME)
        .where(filter=FieldFilter("details.quota", "==", quota))
        .limit(1)
        .stream()
    )

    async for product in product_stream:
        return Product(**product.to_dict())


async def get_active_products_by_product_type_and_category(
    product_type: ProductType,
    product_category: Optional[ProductCategory] = None,
) -> list[Product]:
    products_query = (
        firebase.db.collection(Product.COLLECTION_NAME)
        .where(filter=FieldFilter("is_active", "==", True))
        .where(filter=FieldFilter("type", "==", product_type))
    )

    if product_category:
        products_query = products_query.where(
            filter=FieldFilter("category", "==", product_category)
        )

    products = products_query.order_by("order", direction=Query.ASCENDING).stream()

    return [Product(**product.to_dict()) async for product in products]


async def get_products(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Product]:
    products_query = firebase.db.collection(Product.COLLECTION_NAME)

    if start_date:
        products_query = products_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        products_query = products_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    products = products_query.stream()

    return [Product(**product.to_dict()) async for product in products]
