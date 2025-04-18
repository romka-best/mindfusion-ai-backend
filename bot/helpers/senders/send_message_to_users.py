import asyncio
import logging
import traceback

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiohttp import ClientOSError
from redis.exceptions import ConnectionError

from bot.database.models.user import User
from bot.database.operations.user.getters import get_users_by_language_code
from bot.database.operations.user.updaters import update_user
from bot.locales.types import LanguageCode

BATCH_SIZE = 30
DELAY_SECONDS = 1


async def delayed_send_message_to_user(
    bot: Bot, chat_id: str, text: str, timeout: int, reply_markup=None
):
    await asyncio.sleep(timeout)

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            disable_notification=True,
        )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_message_to_user(
                bot, chat_id, text, e.retry_after + 30, reply_markup
            )
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        asyncio.create_task(
            delayed_send_message_to_user(bot, chat_id, text, 60, reply_markup)
        )
    except TelegramBadRequest as error:
        logging.error(error)
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in delayed_send_message: {error_trace}")


async def send_message_to_user(bot: Bot, user: User, message: str, reply_markup=None):
    try:
        if not user.is_blocked:
            await bot.send_message(
                chat_id=user.telegram_chat_id,
                text=message,
                reply_markup=reply_markup,
                disable_notification=True,
            )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(user.id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_message_to_user(
                bot, user.telegram_chat_id, message, e.retry_after + 30, reply_markup
            )
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        asyncio.create_task(
            delayed_send_message_to_user(
                bot, user.telegram_chat_id, message, 60, reply_markup
            )
        )
    except TelegramBadRequest as error:
        logging.exception(error)
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in send_message: {error_trace}")


async def send_message_to_users(
    bot: Bot,
    user_type: str,
    language_code: LanguageCode,
    message: str,
    reply_markup=None,
):
    users = await get_users_by_language_code(language_code)
    for i in range(0, len(users), BATCH_SIZE):
        batch_users = users[i : i + BATCH_SIZE]

        tasks = []
        for user in batch_users:
            if (
                user_type == "all"
                or (user_type == "free" and not user.subscription_id)
                or (user_type == "paid" and user.subscription_id)
            ):
                tasks.append(send_message_to_user(bot, user, message, reply_markup))

        await asyncio.gather(*tasks, return_exceptions=True)

        if i + BATCH_SIZE < len(users):
            await asyncio.sleep(DELAY_SECONDS)
