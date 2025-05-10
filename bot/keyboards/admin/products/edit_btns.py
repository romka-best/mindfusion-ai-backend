from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class EditBtns(BaseView):
    def render(self, product):
        route = f"admin:products:{product.id}:edit:"

        self.plan_add([
            "not for render",
            {
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✏️ Название",
                                callback_data=route + "name",
                            ),
                            InlineKeyboardButton(
                                text="✏️ Описание",
                                callback_data=route + "desc",
                            ),
                        ],
                        [
                            InlineKeyboardButton(text="✏️ Цена", callback_data=route + "price"),
                            InlineKeyboardButton(
                                text="✏️ Скидка",
                                callback_data=route + "discount",
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="◀️ Назад",
                                callback_data=f"admin:{product.type.lower()}s:index",
                            ),
                        ],
                    ],
                ),
            },
        ])

        return self.plan
