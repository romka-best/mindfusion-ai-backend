from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter, Query

from bot.config import config
from bot.database.main import firebase
from bot.database.models.subscription import Subscription, SubscriptionStatus


async def get_subscription(subscription_id: str) -> Optional[Subscription]:
    if not subscription_id:
        return

    subscription_ref = firebase.db.collection(Subscription.COLLECTION_NAME).document(
        str(subscription_id)
    )
    subscription = await subscription_ref.get()

    if subscription.exists:
        return Subscription(**subscription.to_dict())


async def get_activated_subscriptions_by_user_id(
    user_id: str,
    end_date=datetime,
) -> list[Subscription]:
    subscriptions = (
        firebase.db.collection(Subscription.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .where(filter=FieldFilter("end_date", ">", end_date))
        .where(
            filter=FieldFilter(
                "status",
                "not-in",
                [
                    SubscriptionStatus.WAITING,
                    SubscriptionStatus.ERROR,
                    SubscriptionStatus.DECLINED,
                ],
            )
        )
        .order_by("created_at", direction=Query.DESCENDING)
        .stream()
    )

    return [
        Subscription(**subscription.to_dict()) async for subscription in subscriptions
    ]


async def get_count_of_subscriptions(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[str] = None,
    statuses: Optional[list[SubscriptionStatus]] = None,
) -> int:
    total_subscriptions = set()
    subscriptions_query = firebase.db.collection(Subscription.COLLECTION_NAME)

    if start_date:
        subscriptions_query = subscriptions_query.where(
            filter=FieldFilter("end_date", ">=", start_date)
        )
    if end_date:
        subscriptions_query = subscriptions_query.where(
            filter=FieldFilter("start_date", "<=", end_date)
        )
    if product_id:
        subscriptions_query = subscriptions_query.where(
            filter=FieldFilter("product_id", "==", product_id)
        )
    if statuses is not None:
        subscriptions_query = subscriptions_query.where(
            filter=FieldFilter("status", "in", statuses)
        )

    subscriptions_query = subscriptions_query.limit(config.BATCH_SIZE)

    is_running = True
    last_doc = None

    while is_running:
        if last_doc:
            subscriptions_query = subscriptions_query.start_after(last_doc)

        docs = subscriptions_query.stream()

        count = 0
        async for doc in docs:
            count += 1

            subscription = Subscription(**doc.to_dict())
            total_subscriptions.add(subscription.user_id)

        if count < config.BATCH_SIZE:
            is_running = False
            break

        last_doc = doc

    return len(total_subscriptions)


async def get_subscriptions_by_user_id(user_id: str) -> list[Subscription]:
    subscriptions = (
        firebase.db.collection(Subscription.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .stream()
    )

    return [
        Subscription(**subscription.to_dict()) async for subscription in subscriptions
    ]


async def get_subscription_by_provider_payment_charge_id(
    provider_payment_charge_id: str,
) -> Optional[Subscription]:
    subscription_stream = (
        firebase.db.collection(Subscription.COLLECTION_NAME)
        .where(
            filter=FieldFilter(
                "provider_payment_charge_id", "==", provider_payment_charge_id
            )
        )
        .limit(1)
        .stream()
    )

    async for doc in subscription_stream:
        return Subscription(**doc.to_dict())


async def get_subscription_by_provider_auto_payment_charge_id(
    provider_auto_payment_charge_id: str,
) -> Optional[Subscription]:
    subscription_stream = (
        firebase.db.collection(Subscription.COLLECTION_NAME)
        .where(
            filter=FieldFilter(
                "provider_auto_payment_charge_id", "==", provider_auto_payment_charge_id
            )
        )
        .order_by("created_at", direction=Query.DESCENDING)
        .limit(1)
        .stream()
    )

    async for doc in subscription_stream:
        return Subscription(**doc.to_dict())


async def get_subscriptions(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Subscription]:
    subscriptions_query = firebase.db.collection(Subscription.COLLECTION_NAME)

    if start_date:
        subscriptions_query = subscriptions_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        subscriptions_query = subscriptions_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    subscriptions = subscriptions_query.stream()

    return [
        Subscription(**subscription.to_dict()) async for subscription in subscriptions
    ]


async def get_subscriptions_by_status(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: SubscriptionStatus = None,
) -> list[Subscription]:
    subscriptions_query = firebase.db.collection(Subscription.COLLECTION_NAME).where(
        filter=FieldFilter("status", "==", status)
    )

    if start_date:
        subscriptions_query = subscriptions_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        subscriptions_query = subscriptions_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    subscriptions = subscriptions_query.stream()

    return [
        Subscription(**subscription.to_dict()) async for subscription in subscriptions
    ]
