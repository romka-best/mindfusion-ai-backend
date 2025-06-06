from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class AskValue(BaseView):
    def render(self,  product_type):
        product_type = product_type.lower() + "s"

        self.plan_add(
            [
                "edit_text",
                {
                    "text": "Отправьте размер скидки",
                    "reply_markup": InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="🚫 Отмена",
                                    callback_data=f"admin:{product_type}:index",
                                ),
                            ],
                        ],
                    ),
                },
            ],
        )

        return self.plan
