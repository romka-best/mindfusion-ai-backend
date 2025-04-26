from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.locales.main import get_localization


class Show:
    def render(self, lang_code):
        return {
            "text": get_localization(lang_code).menu_photo_bundle_show(),
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).menu_photo_bundle_show_upload(),
                            callback_data="11|photo_bundles:photos:new"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).menu_photo_bundle_show_edit(),
                            callback_data="11|photo_bundles:photos:edit_mode",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).menu_photo_bundle_delete_one(),
                            callback_data="11|photo_bundles:photos:delete_mode",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).menu_photo_bundle_delete_all(),
                            callback_data="11|photo_bundles:photos:delete_all_confirm",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).menu_photo_bundle_back_to_profile(),
                            callback_data="11|photo_bundles:back_to_profile"
                        ),
                    ],
                ]
            ),
        }
