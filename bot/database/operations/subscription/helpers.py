from typing import Optional

from bot.database.main import firebase
from bot.database.models.common import Currency, PaymentMethod
from bot.database.models.subscription import (
    Subscription,
    SubscriptionPeriod,
    SubscriptionStatus,
)


async def create_subscription_object(
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
    subscription_ref = firebase.db.collection(Subscription.COLLECTION_NAME).document(
        subscription_id
    )
    return Subscription(
        id=subscription_ref.id,
        user_id=user_id,
        product_id=product_id,
        period=period,
        status=status,
        currency=currency,
        amount=amount,
        income_amount=income_amount,
        payment_method=payment_method,
        provider_payment_charge_id=provider_payment_charge_id,
    )
