from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_music_gen_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MUSIC_GEN_SECONDS_10,
                callback_data="music_gen:10",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).MUSIC_GEN_SECONDS_30,
                callback_data="music_gen:30",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MUSIC_GEN_SECONDS_60,
                callback_data="music_gen:60",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).MUSIC_GEN_SECONDS_180,
                callback_data="music_gen:180",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MUSIC_GEN_SECONDS_300,
                callback_data="music_gen:300",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).MUSIC_GEN_SECONDS_600,
                callback_data="music_gen:600",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="music_gen:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
