from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class New:
    def render(self):
        return {
            "text": "Отправьте одну или несколько фотографий",
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад к фотографиям",
                            callback_data="photo_bundles:show",
                        ),
                    ],
                ]
            ),
        }
