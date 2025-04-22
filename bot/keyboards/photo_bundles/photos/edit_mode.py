from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..gallery import Gallery
from bot.database.models.photo_bundle.photo import Photo
from bot.database.models.photo_bundle.photo_placeholdeer import PhotoPlaceholder


class EditMode:
    def render(self, photo_grid: list[Photo | PhotoPlaceholder]):
        return {
            **Gallery().render([photo.tg_id for photo in photo_grid]),
            "text": "Выберите порядковый номер фотографии, которую хотите заменить.",
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    *[
                        [
                            InlineKeyboardButton(
                                text=str(index + 1),
                                callback_data=f"photo_bundles:photos:edit:{index}"
                                if isinstance(photo_grid[index], Photo)
                                else f"photo_bundles:photos:edit_placeholder:{index}",
                            )
                            for col in range(5)
                            for index in [row * 5 + col]
                        ]
                        for row in range(2)
                    ],
                    [
                        InlineKeyboardButton(
                            text="Назад к фотографиям",
                            callback_data="photo_bundles:show",
                        ),
                    ],
                ]
            ),
        }
