from bot.database.main import firebase
from bot.database.models.cart import Cart
from bot.database.operations.cart.helpers import create_cart_object


async def write_cart(user_id: str, items: list[dict]) -> Cart:
    cart = await create_cart_object(user_id, items)
    await (
        firebase.db.collection(Cart.COLLECTION_NAME)
        .document(cart.id)
        .set(cart.to_dict())
    )

    return cart


async def write_cart_in_transaction(
    transaction, user_id: str, items: list[dict]
) -> Cart:
    cart = await create_cart_object(user_id, items)
    transaction.set(
        firebase.db.collection(Cart.COLLECTION_NAME).document(cart.id), cart.to_dict()
    )

    return cart
