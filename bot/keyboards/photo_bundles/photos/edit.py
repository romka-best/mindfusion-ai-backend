from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class Edit:
    def render(self):
        return {
            "text": "Отправьте новую фотографию для замены",
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад к фотографиям",
                            callback_data="photo_bundles:photos:edit_mode",
                        ),
                    ],
                ]
            ),
        }
