from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class AskNewFieldValue(BaseView):
    def render(self, old_value):
        self.plan_add([
            "edit_text",
            {
                "text": f"Старое значение:\n    {old_value}\nОтправьте новое",
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🚫 Отменить",
                                callback_data="admin:products:cancel_update",
                            ),
                        ],
                    ],
                ),
            },
        ])

        return self.plan
