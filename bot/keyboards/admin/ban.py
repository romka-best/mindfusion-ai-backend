from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_ban_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="ban:back",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="ban:cancel",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
