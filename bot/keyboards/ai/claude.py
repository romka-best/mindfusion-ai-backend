from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.common import ClaudeGPTVersion, Model
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_claude_keyboard(
    language_code: LanguageCode, model: Model, model_version: ClaudeGPTVersion
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CLAUDE_3_HAIKU
                + (
                    " ✅"
                    if model == Model.CLAUDE
                    and model_version == ClaudeGPTVersion.V3_Haiku
                    else ""
                ),
                callback_data=f"claude:{ClaudeGPTVersion.V3_Haiku}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CLAUDE_3_SONNET
                + (
                    " ✅"
                    if model == Model.CLAUDE
                    and model_version == ClaudeGPTVersion.V3_Sonnet
                    else ""
                ),
                callback_data=f"claude:{ClaudeGPTVersion.V3_Sonnet}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CLAUDE_3_OPUS
                + (
                    " ✅"
                    if model == Model.CLAUDE
                    and model_version == ClaudeGPTVersion.V3_Opus
                    else ""
                ),
                callback_data=f"claude:{ClaudeGPTVersion.V3_Opus}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
