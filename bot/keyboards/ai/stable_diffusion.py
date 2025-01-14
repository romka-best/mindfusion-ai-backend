from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.common import Model, StableDiffusionVersion
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_stable_diffusion_keyboard(
    language_code: LanguageCode,
    model: Model,
    model_version: StableDiffusionVersion,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).STABLE_DIFFUSION_XL + (
                    ' ✅' if model == Model.STABLE_DIFFUSION and model_version == StableDiffusionVersion.XL else ''
                ),
                callback_data=f'stable_diffusion:{StableDiffusionVersion.XL}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).STABLE_DIFFUSION_3 + (
                    ' ✅' if model == Model.STABLE_DIFFUSION and model_version == StableDiffusionVersion.V3 else ''
                ),
                callback_data=f'stable_diffusion:{StableDiffusionVersion.V3}'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
