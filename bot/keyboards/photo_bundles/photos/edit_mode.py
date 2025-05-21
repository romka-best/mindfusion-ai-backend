from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..gallery import Gallery
from bot.database.models.photo_bundle.photo import Photo
from bot.database.models.photo_bundle.photo_placeholdeer import PhotoPlaceholder
from bot.locales.main import get_localization


class EditMode:
    def render(self, lang_code, photo_grid: list[Photo | PhotoPlaceholder]):
        return {
            **Gallery().render([photo.tg_id for photo in photo_grid]),
            "text": get_localization(lang_code).menu_photo_bundle_edit_mode(),
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    *[
                        [
                            InlineKeyboardButton(
                                text=str(index + 1),
                                callback_data=f"11|photo_bundles:photos:edit:{index}"
                                if isinstance(photo_grid[index], Photo)
                                else f"11|photo_bundles:photos:edit_placeholder:{index}",
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
