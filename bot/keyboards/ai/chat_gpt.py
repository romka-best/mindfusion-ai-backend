from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.common import Model, ChatGPTVersion
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_chat_gpt_keyboard(
    language_code: LanguageCode,
    model: Model,
    model_version: ChatGPTVersion,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_4_OMNI_MINI + (
                    ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V4_Omni_Mini else ''
                ),
                callback_data=f'chat_gpt:{ChatGPTVersion.V4_Omni_Mini}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_4_OMNI + (
                    ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V4_Omni else ''
                ),
                callback_data=f'chat_gpt:{ChatGPTVersion.V4_Omni}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_O_4_MINI + (
                    ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V4_O_Mini else ''
                ),
                callback_data=f'chat_gpt:{ChatGPTVersion.V4_O_Mini}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_O_3 + (
                    ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V3_O else ''
                ),
                callback_data=f'chat_gpt:{ChatGPTVersion.V3_O}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_4_1 + (
                    ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V4_1 else ''
                ),
                callback_data=f'chat_gpt:{ChatGPTVersion.V4_1}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_4_1_MINI + (
                    ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V4_1_Mini else ''
                ),
                callback_data=f'chat_gpt:{ChatGPTVersion.V4_1_Mini}'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
