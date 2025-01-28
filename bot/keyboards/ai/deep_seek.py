from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.common import Model, DeepSeekVersion
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_deep_seek_keyboard(
    language_code: LanguageCode,
    model: Model,
    model_version: DeepSeekVersion,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).DEEP_SEEK_V3 + (
                    ' ✅' if model == Model.DEEP_SEEK and model_version == DeepSeekVersion.V3 else ''
                ),
                callback_data=f'deep_seek:{DeepSeekVersion.V3}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).DEEP_SEEK_R1 + (
                    ' ✅' if model == Model.DEEP_SEEK and model_version == DeepSeekVersion.R1 else ''
                ),
                callback_data=f'deep_seek:{DeepSeekVersion.R1}'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
