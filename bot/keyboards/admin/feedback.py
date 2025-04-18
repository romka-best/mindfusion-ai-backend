from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_manage_feedback_keyboard(
    language_code: LanguageCode, user_id: str, feedback_id: str
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_APPROVE,
                callback_data=f"mf:approve:{user_id}:{feedback_id}",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_DENY,
                callback_data=f"mf:deny:{user_id}:{feedback_id}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
