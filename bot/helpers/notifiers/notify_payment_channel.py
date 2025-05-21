import asyncio
from aiogram.exceptions import TelegramRetryAfter
from bot.config import config


async def notify_payment_channel(bot, text, retry_after=0):
    if retry_after:
        await asyncio.sleep(retry_after)

    try:
        await bot.send_message(
            chat_id=config.ALERT_CHANELS["PAYMENT"],
            text=text
        )
    except TelegramRetryAfter as e:
        asyncio.create_task(
                notify_payment_channel(
                    bot,
                    text,
                    e.retry_after + 30
                )
        )
