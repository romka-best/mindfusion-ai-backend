import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class LoggingMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: dict[str, Any],
    ):
        if message.text:
            text = message.text
        elif message.caption:
            text = message.caption
        else:
            text = None

        logging.info(f"Received message from {message.from_user.id}: {text}")
        await handler(message, data)


class LoggingCallbackQueryMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        callback_query: CallbackQuery,
        data: dict[str, Any],
    ):
        logging.info(
            f"Received callback_query from {callback_query.from_user.id}: {callback_query.data}"
        )
        await handler(callback_query, data)
