from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.product import Product


async def update_product(product_id: str, data: dict):
    product_ref = firebase.db.collection(Product.COLLECTION_NAME).document(product_id)
    data["edited_at"] = datetime.now(timezone.utc)

    await product_ref.update(data)
