from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers.gpt_image.user.settings import Background, Compression, Quality, Size
from bot.locales.main import get_localization


class Edit:
    def _toggle(self, condition):
        return "✅ " if condition else "❌ "

    def render(self, lang_code, size, quality, background, compression, **kwargs):  # noqa: ARG002
        return {
            "text": get_localization(lang_code).SETTINGS,
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).SETTINGS_ASPECT_RATIO,
                            callback_data="void",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=self._toggle(size == size_variant.value)
                            + get_localization(lang_code).generation_setting_image_size(size_variant.name),
                            callback_data=f"oai:gpt-image:settings:update:size:{size_variant.name}",
                        )
                        for size_variant in Size
                        if size_variant != Size.AUTO
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).SETTINGS_QUALITY,
                            callback_data="void",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=self._toggle(quality == quality_variant.value)
                            + get_localization(lang_code).generation_setting_image_quality(quality_variant.name),
                            callback_data=f"oai:gpt-image:settings:update:quality:{quality_variant.name}",
                        )
                        for quality_variant in Quality
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).GENERATION_SETTING_BACKGROUND,
                            callback_data="void",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=self._toggle(background == background_variant.value)
                            + get_localization(lang_code).generation_setting_image_bg(background_variant.name),
                            callback_data=f"oai:gpt-image:settings:update:background:{background_variant.name}",
                        )
                        for background_variant in Background
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).GENERATION_SETTING_OUTPUT_IMAGE_FORMAT,
                            callback_data="void",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=self._toggle(not compression)
                            + get_localization(lang_code).GENERATION_SETTING_OUTPUT_IMAGE_FORMAT_ORIGINAL,
                            callback_data=f"oai:gpt-image:settings:update:compression:{Compression(False).name}",
                        ),
                        InlineKeyboardButton(
                            text=self._toggle(compression)
                            + get_localization(lang_code).GENERATION_SETTING_OUTPUT_IMAGE_FORMAT_COMPRESSED,
                            callback_data=f"oai:gpt-image:settings:update:compression:{Compression(True).name}",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).ACTION_BACK,
                            callback_data="oai:gpt-image:show",
                        ),
                    ],
                ],
            ),
        }
