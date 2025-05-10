from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class EditPrice(BaseView):
    def render(self, product):
        buttons = [
            InlineKeyboardButton(text=currency, callback_data=f"admin:products:{product.id}:anfv:price_{currency}")
            for currency in product.prices
        ]

        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

        self.plan_add([
            "edit_text",
            {
                "text": "Выберите валюту",
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        *keyboard,
                        [
                            InlineKeyboardButton(
                                text="🚫Отменить", callback_data=f"admin:products:{product.id}:cancel_edit",
                            ),
                        ],
                    ],
                ),
            },
        ])

        return self.plan

