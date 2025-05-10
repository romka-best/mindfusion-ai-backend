from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class EditDesc(BaseView):
    def render(self, product):
        buttons = [
            InlineKeyboardButton(text=lang, callback_data=f"admin:products:{product.id}:anfv:desc_{lang}")
            for lang in product.descriptions
        ]

        keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]

        self.plan_add([
            "edit_text",
            {
                "text": "Выберите язык",
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        *keyboard,
                        [
                            InlineKeyboardButton(
                                text="🚫 Отменить", callback_data=f"admin:products:{product.id}:cancel_edit",
                            ),
                        ],
                    ],
                ),
            },
        ])

        return self.plan
