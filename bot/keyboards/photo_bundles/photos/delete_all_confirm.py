from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.locales.main import get_localization


class DeleteAllConfirm:
    def render(self, lang_code):
        return {
            "text": get_localization(lang_code).photo_bundle_delete_all_confirm(),
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="❌",
                            callback_data="1|photo_bundles:show",
                        ),
                        InlineKeyboardButton(
                            text="✅",
                            callback_data="1|photo_bundles:photos:delete_all",
                        ),
                    ],
                ]
            ),
        }
