from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..gallery import Gallery


class DeleteMode:
    def render(self, media, indexes):
        return {
            **Gallery().render(media),
            "text": "Выберите порядковый номер фотографии, которую хотите удалить.",
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    *[
                        [
                            InlineKeyboardButton(
                                text=f"{index + 1}" if index in indexes else "x",
                                callback_data=f"photo_bundles:photos:delete:{index}" if index in indexes else "x"
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
