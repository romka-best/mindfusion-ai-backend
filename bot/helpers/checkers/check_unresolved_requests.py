import asyncio
from datetime import datetime, timezone, timedelta

from aiogram import Bot

from bot.database.models.request import RequestStatus
from bot.database.operations.product.getters import get_product
from bot.database.operations.request.getters import get_started_requests
from bot.database.operations.request.updaters import update_request
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers
from bot.locales.types import LanguageCode


async def check_unresolved_requests(bot: Bot):
    today_utc_day = datetime.now(timezone.utc)
    yesterday_utc_day = today_utc_day - timedelta(days=1)
    not_finished_requests = await get_started_requests(yesterday_utc_day, today_utc_day - timedelta(minutes=30))

    product_ids = set()
    tasks = []
    for not_finished_request in not_finished_requests:
        had_error = True
        not_finished_request.details['has_error'] = had_error
        tasks.append(
            update_request(
                not_finished_request.id,
                {
                    'status': RequestStatus.FINISHED,
                    'details': not_finished_request.details,
                }
            )
        )
        product_ids.add(not_finished_request.product_id)

    product_names = []
    for product_id in product_ids:
        product = await get_product(product_id)
        product_names.append(product.names.get(LanguageCode.EN))

    await asyncio.gather(*tasks)

    if len(tasks):
        await send_message_to_admins_and_developers(
            bot,
            f'⚠️ <b>Внимание!</b>\n\nЯ нашёл генерации, которым больше 30 минут ❗️\n\nКоличество: {len(tasks)}\n\nМодели: {", ".join(product_names)}',
        )
