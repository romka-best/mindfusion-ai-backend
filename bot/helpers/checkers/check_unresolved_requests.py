from datetime import datetime, timezone, timedelta

from aiogram import Bot, Dispatcher

from bot.database.models.request import RequestStatus
from bot.database.operations.product.getters import get_product
from bot.database.operations.request.getters import get_started_requests
from bot.database.operations.request.updaters import update_request
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers
from bot.locales.main import get_user_language, get_localization


async def check_unresolved_requests(bot: Bot, dp: Dispatcher):
    today_utc_day = datetime.now(timezone.utc)
    yesterday_utc_day = today_utc_day - timedelta(days=1)
    not_finished_requests = await get_started_requests(yesterday_utc_day, today_utc_day - timedelta(minutes=30))

    product_names = {}
    count_unresolved_requests = 0
    for not_finished_request in not_finished_requests:
        had_error = True
        not_finished_request.details['has_error'] = had_error

        await update_request(
            not_finished_request.id,
            {
                'status': RequestStatus.FINISHED,
                'details': not_finished_request.details,
            }
        )

        try:
            user_language_code = await get_user_language(str(not_finished_request.user_id), dp.storage)

            if product_names.get(not_finished_request.product_id):
                product_name = product_names.get(not_finished_request.product_id)
            else:
                product = await get_product(not_finished_request.product_id)
                product_name = product.names.get(user_language_code)
                product_names.update({product.id: product_name})

            await bot.send_message(
                chat_id=not_finished_request.user_id,
                text=get_localization(user_language_code).model_unresolved_request(product_name)
            )
        except Exception:
            pass

        count_unresolved_requests += 1

    if count_unresolved_requests > 0:
        await send_message_to_admins_and_developers(
            bot,
            f'⚠️ <b>Внимание!</b>\n\nЯ нашёл генерации, которым больше 30 минут ❗️\n\nКоличество: {len(count_unresolved_requests)}\n\nМодели: {", ".join(product_names.values())}',
        )
