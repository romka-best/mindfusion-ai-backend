from datetime import datetime, timezone

import stripe
from aiogram import Bot
from google.cloud import firestore

from bot.database.models.common import PaymentMethod
from bot.database.models.subscription import Subscription, SubscriptionStatus
from bot.database.operations.product.getters import get_product
from bot.database.operations.subscription.updaters import update_subscription_in_transaction
from bot.helpers.senders.send_message_to_admins import send_message_to_admins
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


@firestore.async_transactional
async def unsubscribe_wrapper(transaction, old_subscription: Subscription, bot: Bot):
    await unsubscribe(transaction, old_subscription, bot)


async def unsubscribe(transaction, old_subscription: Subscription, bot: Bot):
    current_date = datetime.now(timezone.utc)

    await update_subscription_in_transaction(transaction, old_subscription.id, {
        'status': SubscriptionStatus.CANCELED,
        'end_date': current_date if old_subscription.status == SubscriptionStatus.TRIAL else old_subscription.end_date,
    })

    if old_subscription.payment_method == PaymentMethod.STRIPE:
        await stripe.Subscription.modify_async(
            old_subscription.stripe_id,
            cancel_at_period_end=True,
        )
    elif old_subscription.payment_method == PaymentMethod.TELEGRAM_STARS:
        await bot.edit_user_star_subscription(
            user_id=int(old_subscription.user_id),
            telegram_payment_charge_id=old_subscription.provider_payment_charge_id,
            is_canceled=True,
        )

    product = await get_product(old_subscription.product_id)

    if old_subscription.status == SubscriptionStatus.TRIAL:
        await send_message_to_admins(
            bot=bot,
            message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                status=SubscriptionStatus.CANCELED,
                subscription=old_subscription,
                product=product,
                is_trial=True,
            )
        )
    else:
        await send_message_to_admins(
            bot=bot,
            message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                status=SubscriptionStatus.CANCELED,
                subscription=old_subscription,
                product=product,
                is_trial=False,
            )
        )
