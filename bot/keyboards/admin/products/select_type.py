from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class SelectType(BaseView):
    def render(self):
        self.plan_add([
            "edit_text",
            {
                "text": "Выберите тип продукта",
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="💳 Подписки",
                                callback_data="admin:subscriptions:index",
                            ),
                        ],
                        [InlineKeyboardButton(text="🛍 Пакеты", callback_data="admin:packages:index")],
                        [
                            InlineKeyboardButton(
                                text="◀️ Назад",
                                callback_data="admin:products:back_to_admin",
                            ),
                        ],
                    ],
                ),
            },
        ])

        return self.plan
