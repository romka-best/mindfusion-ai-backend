from aiogram import Bot

from bot.handlers.admin.statistics_handler import handle_get_statistics
from bot.locales.types import LanguageCode
from bot.helpers.notifiers.notify_statistic_channel import notify_statistic_channel

async def send_statistics(bot: Bot, period='day'):
    texts = await handle_get_statistics(LanguageCode.RU, period)

    keys = [
        "users",
        "text_models",
        "summary_models",
        "image_models",
        "music_models",
        "video_models",
        "reactions",
        "bonuses",
        "ai_expenses",
        "tech_expenses",
        "user_expenses",
        "expenses",
        "incomes",
    ]

    for key in keys:
        await notify_statistic_channel(bot, texts.get(key))
