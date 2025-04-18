from aiogram import Bot

from bot.handlers.admin.statistics_handler import handle_get_statistics
from bot.helpers.senders.send_message_to_admins import send_message_to_admins
from bot.helpers.senders.send_message_to_super_admin import send_message_to_super_admin
from bot.locales.types import LanguageCode


async def send_statistics(bot: Bot, period="day"):
    texts = await handle_get_statistics(LanguageCode.RU, period)

    await send_message_to_admins(bot, texts.get("users"))
    await send_message_to_super_admin(bot, texts.get("text_models"))
    await send_message_to_super_admin(bot, texts.get("summary_models"))
    await send_message_to_super_admin(bot, texts.get("image_models"))
    await send_message_to_super_admin(bot, texts.get("music_models"))
    await send_message_to_super_admin(bot, texts.get("video_models"))
    await send_message_to_super_admin(bot, texts.get("reactions"))
    await send_message_to_super_admin(bot, texts.get("bonuses"))
    await send_message_to_admins(bot, texts.get("ai_expenses"))
    await send_message_to_admins(bot, texts.get("tech_expenses"))
    await send_message_to_admins(bot, texts.get("user_expenses"))
    await send_message_to_admins(bot, texts.get("expenses"))
    await send_message_to_admins(bot, texts.get("incomes"))
