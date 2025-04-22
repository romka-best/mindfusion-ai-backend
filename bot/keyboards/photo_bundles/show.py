from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class Show:
    def render(self):
        return {
            "text": "Действия",
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Загрузить", callback_data="photo_bundles:photos:new"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Заменить одну",
                            callback_data="photo_bundles:photos:edit_mode",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Удалить одну",
                            callback_data="photo_bundles:photos:delete_mode",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Удалить все",
                            callback_data="photo_bundles:photos:delete_all_confirm",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Назад в профиль", callback_data="photo_bundles:back_to_profile"
                        ),
                    ],
                ]
            ),
        }
