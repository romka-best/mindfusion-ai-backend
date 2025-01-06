import asyncio
from datetime import datetime, timezone, timedelta

from aiogram import Bot

from bot.database.models.subscription import SubscriptionStatus
from bot.database.operations.product.getters import get_product
from bot.database.operations.subscription.getters import get_subscriptions_by_status
from bot.database.operations.subscription.updaters import update_subscription
from bot.helpers.senders.send_message_to_admins import send_message_to_admins
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


async def check_waiting_payments(bot: Bot):
    today_utc_day = datetime.now(timezone.utc)
    yesterday_utc_day = today_utc_day - timedelta(days=1)
    not_finished_subscriptions = await get_subscriptions_by_status(
        yesterday_utc_day,
        today_utc_day - timedelta(hours=1),
        SubscriptionStatus.WAITING,
    )

    tasks = []
    for not_finished_subscription in not_finished_subscriptions:
        status = SubscriptionStatus.DECLINED
        not_finished_subscription.status = status
        tasks.append(
            update_subscription(
                not_finished_subscription.id,
                {
                    'status': not_finished_subscription.status,
                }
            )
        )

        product = await get_product(not_finished_subscription.product_id)
        await send_message_to_admins(
            bot=bot,
            message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                status=SubscriptionStatus.DECLINED,
                subscription=not_finished_subscription,
                product=product,
            ),
        )

    await asyncio.gather(*tasks)
