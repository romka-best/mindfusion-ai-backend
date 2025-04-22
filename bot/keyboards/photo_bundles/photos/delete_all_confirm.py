from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class DeleteAllConfirm:
    def render(self):
        return {
            "text": "Вы уверены, что хотите удалить ВСЕ фотографии?",
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Нет",
                            callback_data="photo_bundles:show",
                        ),
                        InlineKeyboardButton(
                            text="Да",
                            callback_data="photo_bundles:photos:delete_all",
                        ),
                    ],
                ]
            ),
        }
