from datetime import timedelta

import stripe
from aiogram import Bot
from google.cloud import firestore

from bot.database.models.common import PaymentMethod
from bot.database.models.subscription import (
    Subscription,
    SubscriptionPeriod,
    SubscriptionStatus,
)
from bot.database.operations.product.getters import get_product
from bot.database.operations.subscription.updaters import (
    update_subscription_in_transaction,
)
from bot.helpers.senders.send_message_to_admins import send_message_to_admins
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


@firestore.async_transactional
async def resubscribe_wrapper(transaction, old_subscription: Subscription, bot: Bot):
    await resubscribe(transaction, old_subscription, bot)


async def resubscribe(transaction, old_subscription: Subscription, bot: Bot):
    is_trial = (old_subscription.end_date - old_subscription.start_date).days <= 3
    if is_trial and old_subscription.period == SubscriptionPeriod.MONTH1:
        old_subscription.end_date = old_subscription.start_date + timedelta(days=30)
    elif is_trial and old_subscription.period == SubscriptionPeriod.MONTHS12:
        old_subscription.end_date = old_subscription.start_date + timedelta(days=365)

    await update_subscription_in_transaction(
        transaction,
        old_subscription.id,
        {
            "status": SubscriptionStatus.TRIAL
            if is_trial
            else SubscriptionStatus.ACTIVE,
            "end_date": old_subscription.end_date,
        },
    )

    if old_subscription.payment_method == PaymentMethod.STRIPE:
        await stripe.Subscription.modify_async(
            old_subscription.stripe_id, cancel_at_period_end=False
        )
    elif old_subscription.payment_method == PaymentMethod.TELEGRAM_STARS:
        await bot.edit_user_star_subscription(
            user_id=int(old_subscription.user_id),
            telegram_payment_charge_id=old_subscription.provider_payment_charge_id,
            is_canceled=False,
        )

    product = await get_product(old_subscription.product_id)

    if is_trial:
        await send_message_to_admins(
            bot=bot,
            message=get_localization(
                LanguageCode.RU
            ).admin_payment_subscription_changed_status(
                status=SubscriptionStatus.RESUBSCRIBED,
                subscription=old_subscription,
                product=product,
                is_trial=True,
            ),
        )
    else:
        await send_message_to_admins(
            bot=bot,
            message=get_localization(
                LanguageCode.RU
            ).admin_payment_subscription_changed_status(
                status=SubscriptionStatus.RESUBSCRIBED,
                subscription=old_subscription,
                product=product,
                is_trial=False,
            ),
        )
