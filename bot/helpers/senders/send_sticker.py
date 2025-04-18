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

from bot.database.operations.user.updaters import update_user


async def delayed_send_sticker(bot: Bot, chat_id: str, sticker_id: str, timeout: int):
    await asyncio.sleep(timeout)

    try:
        await bot.send_sticker(
            chat_id=chat_id,
            sticker=sticker_id,
            disable_notification=True,
        )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_sticker(bot, chat_id, sticker_id, e.retry_after + 30)
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        asyncio.create_task(delayed_send_sticker(bot, chat_id, sticker_id, 60))
    except TelegramBadRequest as error:
        logging.exception(error)
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in delayed_send_sticker: {error_trace}")


async def send_sticker(
    bot: Bot,
    chat_id: str,
    sticker_id: str,
):
    try:
        await bot.send_sticker(
            chat_id=chat_id,
            sticker=sticker_id,
            disable_notification=True,
        )
    except TelegramForbiddenError:
        await update_user(
            chat_id,
            {
                "is_blocked": True,
            },
        )
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_sticker(bot, chat_id, sticker_id, e.retry_after + 30)
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        asyncio.create_task(delayed_send_sticker(bot, chat_id, sticker_id, 60))
    except TelegramBadRequest as error:
        logging.exception(error)
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in send_sticker: {error_trace}")
