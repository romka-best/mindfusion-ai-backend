from google.cloud import firestore

from bot.database.models.common import Quota
from bot.database.models.user import User
from bot.database.operations.message.writers import write_message_in_transaction
from bot.helpers.updaters.update_user_usage_quota import (
    update_user_usage_quota_in_transaction,
)


@firestore.async_transactional
async def create_new_message_and_update_user(
    transaction, role: str, content: str, user: User, user_quota: Quota
):
    await write_message_in_transaction(
        transaction, user.current_chat_id, role, "", content
    )

    await update_user_usage_quota_in_transaction(transaction, user, user_quota, 1)
