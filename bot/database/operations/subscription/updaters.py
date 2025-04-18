from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.subscription import Subscription


async def update_subscription(subscription_id: str, data: dict):
    subscription_ref = firebase.db.collection(Subscription.COLLECTION_NAME).document(
        subscription_id
    )
    data["edited_at"] = datetime.now(timezone.utc)

    await subscription_ref.update(data)


async def update_subscription_in_transaction(
    transaction, subscription_id: str, data: dict
):
    data["edited_at"] = datetime.now(timezone.utc)

    transaction.update(
        firebase.db.collection(Subscription.COLLECTION_NAME).document(subscription_id),
        data,
    )
