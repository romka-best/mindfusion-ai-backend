from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class New(BaseView):
    def render(self):
        self.plan_add([
            "edit_text",
            {
                "text": "Введите id пользователя",
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🚫 Отменить",
                                callback_data="admin:subscriptions:refund:cancel_action",
                            ),
                        ],
                    ],
                ),
            },
        ])

        return self.plan
