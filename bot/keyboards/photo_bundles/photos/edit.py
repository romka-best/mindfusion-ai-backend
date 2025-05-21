from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.locales.main import get_localization


class Edit:
    def render(self, lang_code):
        return {
            "text": get_localization(lang_code).menu_photo_bundle_edit(),
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).menu_photo_bundle_back_to_photos(),
                            callback_data="1|photo_bundles:photos:edit_mode",
                        ),
                    ],
                ]
            ),
        }
