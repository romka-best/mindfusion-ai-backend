from typing import Optional

from aiogram.types import User as TelegramUser

from bot.database.main import firebase
from bot.database.models.common import Quota
from bot.database.models.user import User
from bot.database.operations.user.helpers import create_user_object


async def write_user_in_transaction(
    transaction,
    telegram_user: TelegramUser,
    chat_id: str,
    telegram_chat_id: str,
    stripe_id: str,
    referred_by: Optional[str],
    is_referred_by_user=False,
    quota=Quota.CHAT_GPT4_OMNI_MINI,
    utm=None,
    discount=0,
) -> User:
    user_ref = firebase.db.collection(User.COLLECTION_NAME).document(str(telegram_user.id))
    user_data = (await user_ref.get()).to_dict() or {}

    created_user = create_user_object(
        telegram_user,
        user_data,
        chat_id,
        telegram_chat_id,
        stripe_id,
        referred_by,
        is_referred_by_user,
        quota,
        utm,
        discount,
    )

    transaction.set(user_ref, created_user.to_dict())

    return created_user
