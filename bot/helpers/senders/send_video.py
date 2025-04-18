import asyncio
import logging
import traceback

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import Message, URLInputFile
from aiohttp import ClientOSError
from redis.exceptions import ConnectionError

from bot.database.operations.user.updaters import update_user
from bot.helpers.senders.send_error_info import send_error_info


async def delayed_send_video(
    bot: Bot,
    chat_id: str,
    result: str,
    caption: str,
    filename: str,
    duration: int,
    timeout: int,
    reply_markup=None,
    reply_to_message_id=None,
    parse_mode=ParseMode.HTML,
) -> Message:
    await asyncio.sleep(timeout)

    answered_message = None

    try:
        answered_message = await bot.send_video(
            chat_id=chat_id,
            video=URLInputFile(result, filename=filename, timeout=300),
            caption=caption,
            duration=duration,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
            parse_mode=parse_mode,
        )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        answered_message = await delayed_send_video(
            bot,
            chat_id,
            result,
            caption,
            filename,
            duration,
            e.retry_after + 30,
            reply_markup,
            reply_to_message_id,
            parse_mode,
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        answered_message = await delayed_send_video(
            bot,
            chat_id,
            result,
            caption,
            filename,
            duration,
            60,
            reply_markup,
            reply_to_message_id,
            parse_mode,
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in delayed_send_video: {error_trace}")

        answered_message = await bot.send_message(
            chat_id=chat_id,
            reply_markup=reply_markup,
            text=result,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )

        await send_error_info(bot=bot, user_id=chat_id, info=str(e), hashtags=["video"])

    return answered_message


async def send_video(
    bot: Bot,
    chat_id: str,
    result: str,
    caption: str,
    filename: str,
    duration: int,
    width=None,
    height=None,
    reply_markup=None,
    reply_to_message_id=None,
    parse_mode=ParseMode.HTML,
) -> Message:
    answered_message = None

    try:
        answered_message = await bot.send_video(
            chat_id=chat_id,
            video=URLInputFile(result, filename=filename, timeout=300),
            caption=caption,
            duration=duration,
            width=width,
            height=height,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
            parse_mode=parse_mode,
        )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        answered_message = await delayed_send_video(
            bot,
            chat_id,
            result,
            caption,
            filename,
            duration,
            e.retry_after + 30,
            reply_markup,
            reply_to_message_id,
            parse_mode,
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        answered_message = await delayed_send_video(
            bot,
            chat_id,
            result,
            caption,
            filename,
            duration,
            60,
            reply_markup,
            reply_to_message_id,
            parse_mode,
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in send_video: {error_trace}")

        answered_message = await bot.send_message(
            chat_id=chat_id,
            reply_markup=reply_markup,
            text=result,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )

        await send_error_info(bot=bot, user_id=chat_id, info=str(e), hashtags=["video"])

    return answered_message
