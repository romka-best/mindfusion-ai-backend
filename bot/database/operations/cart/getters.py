from typing import Optional

from google.cloud.firestore_v1 import FieldFilter

from bot.database.main import firebase
from bot.database.models.cart import Cart


async def get_cart(cart_id: str) -> Optional[Cart]:
    cart_ref = firebase.db.collection(Cart.COLLECTION_NAME).document(str(cart_id))
    cart = await cart_ref.get()

    if cart.exists:
        return Cart(**cart.to_dict())
    return None


async def get_cart_by_user_id(user_id: str) -> Optional[Cart]:
    cart_stream = (
        firebase.db.collection(Cart.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .limit(1)
        .stream()
    )

    async for doc in cart_stream:
        return Cart(**doc.to_dict())
