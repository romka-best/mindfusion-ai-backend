from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.common import FluxVersion, Model
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_flux_keyboard(
    language_code: LanguageCode,
    model: Model,
    model_version: FluxVersion,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).FLUX_1_DEV
                + (
                    " ✅"
                    if model == Model.FLUX and model_version == FluxVersion.V1_Dev
                    else ""
                ),
                callback_data=f"flux:{FluxVersion.V1_Dev}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).FLUX_1_PRO
                + (
                    " ✅"
                    if model == Model.FLUX and model_version == FluxVersion.V1_Pro
                    else ""
                ),
                callback_data=f"flux:{FluxVersion.V1_Pro}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
