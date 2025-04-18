from aiogram.types import Update

from bot.database.operations.user.updaters import update_user


async def handle_forbidden_error(telegram_update: Update):
    user_id = None
    if telegram_update.callback_query and telegram_update.callback_query.from_user.id:
        user_id = str(telegram_update.callback_query.from_user.id)
    elif telegram_update.message and telegram_update.message.from_user.id:
        user_id = str(telegram_update.message.from_user.id)

    if user_id:
        await update_user(
            user_id,
            {
                "is_blocked": True,
            },
        )
