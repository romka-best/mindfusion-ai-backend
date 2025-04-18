from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.common import SunoMode
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_suno_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SUNO_SIMPLE_MODE,
                callback_data=f"suno:{SunoMode.SIMPLE}",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).SUNO_CUSTOM_MODE,
                callback_data=f"suno:{SunoMode.CUSTOM}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_suno_simple_mode_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="suno_simple_mode:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_suno_custom_mode_lyrics_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SUNO_SKIP,
                callback_data="suno_custom_mode_lyrics:skip",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="suno_custom_mode_lyrics:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_suno_custom_mode_genres_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SUNO_START_AGAIN,
                callback_data="suno_custom_mode_genres:start_again",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
