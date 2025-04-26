from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..gallery import Gallery
from bot.locales.main import get_localization


class DeleteMode:
    def render(self, lang_code, media, indexes):
        return {
            **Gallery().render(media),
            "text": get_localization(lang_code).menu_photo_bundle_delete_mode(),
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    *[
                        [
                            InlineKeyboardButton(
                                text=f"{index + 1}" if index in indexes else "❌",
                                callback_data=f"11|photo_bundles:photos:delete:{index}" if index in indexes else "x"
                            )
                            for col in range(5)
                            for index in [row * 5 + col]
                        ]
                        for row in range(2)
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).menu_photo_bundle_back_to_photos(),
                            callback_data="11|photo_bundles:show",
                        ),
                    ],
                ]
            ),
        }
