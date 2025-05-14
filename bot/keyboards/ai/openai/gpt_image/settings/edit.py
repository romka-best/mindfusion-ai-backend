from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers.gpt_image.user.settings import Background, Compression, Quality, Size
from bot.locales.main import get_localization


class Edit:
    def _toggle(self, condition):
        return "✅ " if condition else "❌ "

    def render(self, lang_code, size, quality, background, compression, **kwargs):  # noqa: ARG002
        return {
            "text": "Настройки",  # TODO loc
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
                            text=self._toggle(size == size_variant.value) + size_variant.name.capitalize(),  # TODO loc
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
                            text=self._toggle(quality == quality_variant.value) + quality_variant.name.capitalize(),
                            callback_data=f"oai:gpt-image:settings:update:quality:{quality_variant.name}",
                        )
                        for quality_variant in Quality
                    ],
                    [
                        InlineKeyboardButton(
                            text="🖼️ Фон изображения",  # TODO loc
                            callback_data="void",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=self._toggle(background == background_variant.value) + background_variant.name.capitalize(),
                            callback_data=f"oai:gpt-image:settings:update:background:{background_variant.name}",
                        )
                        for background_variant in Background
                    ],
                    [
                        InlineKeyboardButton(
                            text="📷 Формат изображения",  # TODO loc
                            callback_data="void",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=self._toggle(not compression) + "Оригинал",  # TODO loc
                            callback_data=f"oai:gpt-image:settings:update:compression:{Compression(False).name}",
                        ),
                        InlineKeyboardButton(
                            text=self._toggle(compression) + "Сжатый",  # TODO loc
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
