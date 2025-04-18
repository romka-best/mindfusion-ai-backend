from typing import Optional

from bot.database.main import firebase
from bot.database.models.common import Currency, PaymentMethod
from bot.database.models.subscription import (
    Subscription,
    SubscriptionPeriod,
    SubscriptionStatus,
)
from bot.database.operations.subscription.helpers import create_subscription_object


async def write_subscription(
    subscription_id: Optional[str],
    user_id: str,
    product_id: str,
    period: SubscriptionPeriod,
    status: SubscriptionStatus,
    currency: Currency,
    amount: float,
    income_amount: float,
    payment_method: PaymentMethod,
    provider_payment_charge_id: Optional[str] = None,
) -> Subscription:
    subscription = await create_subscription_object(
        subscription_id,
        user_id,
        product_id,
        period,
        status,
        currency,
        amount,
        income_amount,
        payment_method,
        provider_payment_charge_id,
    )

    await (
        firebase.db.collection(Subscription.COLLECTION_NAME)
        .document(subscription.id)
        .set(subscription.to_dict())
    )

    return subscription
