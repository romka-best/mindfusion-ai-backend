from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class Index(BaseView):
    def render(self, products):
        self.plan_add(
            [
                "edit_text",
                {
                    "text": "Пакеты",
                    "reply_markup": InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="⚙️ Массовая скидка",
                                    callback_data="admin:products:bulk_discount",
                                ),
                            ],
                            *[
                                [
                                    InlineKeyboardButton(
                                        text=product.names["ru"],
                                        callback_data=f"admin:products:{product.id}:edit",
                                    ),
                                ]
                                for product in products  # WARNING: tg has limit 100 btns rows per msg
                            ],
                            [
                                InlineKeyboardButton(
                                    text="◀️ Назад",
                                    callback_data="admin:products:select_type",
                                ),
                            ],
                        ],
                    ),
                },
            ],
        )

        return self.plan
