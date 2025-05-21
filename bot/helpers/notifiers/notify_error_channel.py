import asyncio
from aiogram.exceptions import TelegramRetryAfter
from bot.config import config

MAX_MESSAGE_LENGTH = 4096
MAX_TRACE_MESSAGE_LENGTH = 3900

async def notify_error_channel(
    bot,
    user_id,
    info: str = "",
    stack_trace: str = "",
    context: dict = None,
    hashtags: list[str] = None,
    retry_after: int = 0,
):
    if context is None:
        context = {}
    if hashtags is None:
        hashtags = ["error"]

    if retry_after:
        await asyncio.sleep(retry_after)

    try:
        context_text = "\n".join(f"{k}: {v}" for k, v in context.items()) if context else "нет"

        header_text = f"""
#{' #'.join(hashtags)}

🚨 ALARM! Ошибка у пользователя: {user_id}

Информация:
{info}

Контекст:
{context_text}
""".strip()

        await bot.send_message(
            chat_id=config.ALERT_CHANELS["ERROR"],
            text=header_text,
        )

        if stack_trace:
            trace_message = f"Stack trace:\n{stack_trace[:MAX_TRACE_MESSAGE_LENGTH]}"
            await bot.send_message(
                chat_id=config.ALERT_CHANELS["ERROR"],
                text=trace_message,
                parse_mode=None
            )

    except TelegramRetryAfter as e:
        retry_after = e.retry_after + 30
        asyncio.create_task(
            notify_error_channel(
                bot=bot,
                user_id=user_id,
                info=info,
                stack_trace=stack_trace,
                context=context,
                hashtags=hashtags,
                retry_after=retry_after,
            )
        )
