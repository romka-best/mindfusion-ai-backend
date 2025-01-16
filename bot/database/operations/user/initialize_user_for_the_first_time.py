from typing import Optional

import stripe
from firebase_admin.exceptions import AlreadyExistsError
from google.cloud import firestore

from bot.database.main import firebase
from bot.database.models.common import Quota
from bot.database.models.user import User
from bot.database.operations.cart.writers import write_cart_in_transaction
from bot.database.operations.chat.writers import write_chat_in_transaction
from bot.database.operations.user.writers import write_user_in_transaction


@firestore.async_transactional
async def initialize_user_for_the_first_time(
    transaction,
    telegram_user: User,
    telegram_chat_id: str,
    title: str,
    referred_by: Optional[str],
    is_referred_by_user=False,
    quota=Quota.CHAT_GPT4_OMNI_MINI,
    utm=None,
    discount=0,
):
    full_name = telegram_user.first_name
    if telegram_user.last_name:
        full_name += f' {telegram_user.last_name}'
    # create user in stripe
    stripe_customer = await stripe.Customer.create_async(
        name=full_name,
    )

    await write_cart_in_transaction(transaction, str(telegram_user.id), [])
    chat = await write_chat_in_transaction(transaction, str(telegram_user.id), telegram_chat_id, title)
    user = await write_user_in_transaction(
        transaction,
        telegram_user,
        chat.id,
        telegram_chat_id,
        stripe_customer.id,
        referred_by,
        is_referred_by_user,
        quota,
        utm,
        discount,
    )

    # create user in firebase
    try:
        await firebase.create_user(
            uid=user.id,
            display_name=full_name,
        )
    except AlreadyExistsError:
        pass

    return user
