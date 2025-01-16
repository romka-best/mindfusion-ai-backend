import asyncio
import logging
import traceback

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Update

from bot.config import config, MessageSticker
from bot.database.main import firebase
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.initialize_user_for_the_first_time import initialize_user_for_the_first_time
from bot.helpers.senders.send_error_info import send_error_info
from bot.keyboards.common.common import build_error_keyboard, build_start_keyboard
from bot.locales.main import get_localization, get_user_language, set_user_language


async def delayed_notify_admins_about_error(
    bot: Bot,
    telegram_update: Update,
    dp: Dispatcher,
    error_info,
    timeout: int,
):
    await asyncio.sleep(timeout)

    await notify_admins_about_error(bot, telegram_update, dp, error_info)


async def notify_admins_about_error(bot: Bot, telegram_update: Update, dp: Dispatcher, error_info):
    try:
        user_id = None
        if telegram_update.callback_query and telegram_update.callback_query.from_user.id:
            user_id = str(telegram_update.callback_query.from_user.id)
        elif telegram_update.message and telegram_update.message.from_user.id:
            user_id = str(telegram_update.message.from_user.id)

        if user_id:
            user = await get_user(user_id)
            if not user:
                if telegram_update.callback_query:
                    language_code = telegram_update.callback_query.from_user.language_code
                    telegram_user = telegram_update.callback_query.from_user
                    chat_id = str(telegram_update.callback_query.message.chat.id)
                elif telegram_update.message:
                    language_code = telegram_update.message.from_user.language_code
                    telegram_user = telegram_update.message.from_user
                    chat_id = str(telegram_update.message.chat.id)
                else:
                    raise

                language_code = await set_user_language(user_id, language_code, dp.storage)

                chat_title = get_localization(language_code).CHAT_DEFAULT_TITLE
                transaction = firebase.db.transaction()
                await initialize_user_for_the_first_time(
                    transaction,
                    telegram_user,
                    chat_id,
                    chat_title,
                    None,
                    False,
                )
                user_language_code = await get_user_language(user_id, dp.storage)

                greeting = get_localization(user_language_code).START_INFO
                reply_markup = build_start_keyboard(user_language_code)
                await bot.send_message(
                    chat_id=chat_id,
                    text=greeting,
                    reply_markup=reply_markup,
                )
            else:
                await bot.send_sticker(
                    chat_id=user.telegram_chat_id,
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
                )

                reply_markup = build_error_keyboard(user.interface_language_code)
                await bot.send_message(
                    chat_id=user.telegram_chat_id,
                    text=get_localization(user.interface_language_code).ERROR,
                    reply_markup=reply_markup,
                )

                await send_error_info(
                    bot=bot,
                    user_id=user.id,
                    info=error_info,
                )
    except TelegramRetryAfter as e:
        asyncio.create_task(delayed_notify_admins_about_error(bot, telegram_update, dp, error_info, e.retry_after + 30))
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.exception(f'Error in notify_admins_about_error: {error_trace}')

        await send_error_info(
            bot=bot,
            user_id='UNKNOWN',
            info=f'Неизвестная ошибка: {e}',
        )
