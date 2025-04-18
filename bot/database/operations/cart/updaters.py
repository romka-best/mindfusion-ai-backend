from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.cart import Cart


async def update_cart(cart_id: str, data: dict) -> None:
    cart_ref = firebase.db.collection(Cart.COLLECTION_NAME).document(cart_id)
    data["edited_at"] = datetime.now(timezone.utc)

    await cart_ref.update(data)
