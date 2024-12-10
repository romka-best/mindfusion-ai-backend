import asyncio
import logging
import traceback

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter, TelegramNetworkError
from aiogram import Bot
from aiohttp import ClientOSError
from redis.exceptions import ConnectionError

from bot.config import config


async def delayed_send_message_to_super_admin(bot: Bot, text: str, parse_mode: str, timeout: int):
    await asyncio.sleep(timeout)

    try:
        await bot.send_message(
            chat_id=config.SUPER_ADMIN_ID,
            text=text,
            parse_mode=parse_mode,
        )
    except (TelegramBadRequest, TelegramForbiddenError) as error:
        logging.error(error)
    except TelegramRetryAfter as e:
        asyncio.create_task(delayed_send_message_to_super_admin(bot, text, parse_mode, e.retry_after + 30))
    except (ConnectionResetError, OSError, ClientOSError, ConnectionError, TelegramNetworkError):
        asyncio.create_task(
            delayed_send_message_to_super_admin(bot, text, parse_mode, 60)
        )
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f'Error in delayed_send_message_to_super_admin: {error_trace}')


async def send_message_to_super_admin(bot: Bot, message: str, parse_mode='HTML'):
    try:
        await bot.send_message(
            chat_id=config.SUPER_ADMIN_ID,
            text=message,
            parse_mode=parse_mode,
        )
    except (TelegramBadRequest, TelegramForbiddenError) as error:
        logging.error(error)
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_message_to_super_admin(bot, message, parse_mode, e.retry_after + 30)
        )
    except (ConnectionResetError, OSError, ClientOSError, ConnectionError, TelegramNetworkError):
        asyncio.create_task(
            delayed_send_message_to_super_admin(bot, message, parse_mode, 60)
        )
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f'Error in send_message_to_super_admin: {error_trace}')
