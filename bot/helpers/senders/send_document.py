import asyncio
import logging
import traceback
import uuid

from aiogram import Bot
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import URLInputFile
from aiohttp import ClientOSError
from redis.exceptions import ConnectionError

from bot.database.operations.user.updaters import update_user
from bot.helpers.senders.send_error_info import send_error_info


async def delayed_send_document(
    bot: Bot,
    chat_id: str,
    document: str,
    timeout: int,
    reply_markup=None,
    caption=None,
    reply_to_message_id=None,
):
    await asyncio.sleep(timeout)

    try:
        extension = document.rsplit(".", 1)[-1]
        await bot.send_document(
            chat_id=chat_id,
            document=URLInputFile(
                document, filename=f"{uuid.uuid4()}.{extension}", timeout=300
            ),
            reply_markup=reply_markup,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_document(
                bot,
                chat_id,
                document,
                e.retry_after + 30,
                reply_markup,
                caption,
                reply_to_message_id,
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
            delayed_send_document(
                bot, chat_id, document, 60, reply_markup, caption, reply_to_message_id
            )
        )
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in delayed_send_document: {error_trace}")


async def send_document(
    bot: Bot,
    chat_id: str,
    document: str,
    reply_markup=None,
    caption=None,
    reply_to_message_id=None,
):
    try:
        extension = document.rsplit(".", 1)[-1]
        await bot.send_document(
            chat_id=chat_id,
            document=URLInputFile(
                document, filename=f"{uuid.uuid4()}.{extension}", timeout=300
            ),
            reply_markup=reply_markup,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_document(
                bot,
                chat_id,
                document,
                e.retry_after + 30,
                reply_markup,
                caption,
                reply_to_message_id,
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
            delayed_send_document(
                bot, chat_id, document, 60, reply_markup, caption, reply_to_message_id
            )
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Error in send_document: {error_trace}")

        await bot.send_message(
            chat_id=chat_id,
            reply_markup=reply_markup,
            text=document,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )

        await send_error_info(
            bot=bot,
            user_id=chat_id,
            info=str(e),
            hashtags=["document"],
        )
