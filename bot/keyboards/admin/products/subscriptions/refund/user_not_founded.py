from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class UserNotFounded(BaseView):
    def render(self, user_id):
        self.plan_add([
            "answer",
            {
                "text": f"⚠️ Пользователя с id: {user_id} не найден",
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Ввести другой id",
                                callback_data="admin:subscriptions:refund:new",
                            ),
                        ],
                    ],
                ),
            },
        ])

        return self.plan
