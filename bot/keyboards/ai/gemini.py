from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.common import Model, GeminiGPTVersion
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_gemini_keyboard(language_code: LanguageCode, model: Model, model_version: GeminiGPTVersion) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI_2_FLASH + (
                    ' ✅' if model == Model.GEMINI and model_version == GeminiGPTVersion.V2_Flash else ''
                ),
                callback_data=f'gemini:{GeminiGPTVersion.V2_Flash}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI_2_PRO + (
                    ' ✅' if model == Model.GEMINI and model_version == GeminiGPTVersion.V2_Pro else ''
                ),
                callback_data=f'gemini:{GeminiGPTVersion.V2_Pro}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI_1_ULTRA + (
                    ' ✅' if model == Model.GEMINI and model_version == GeminiGPTVersion.V1_Ultra else ''
                ),
                callback_data=f'gemini:{GeminiGPTVersion.V1_Ultra}'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
