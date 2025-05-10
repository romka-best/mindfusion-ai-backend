from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.base_view import BaseView


class Confirm(BaseView):
    def render(self, subscription):
        self.plan_add([
            "edit_text",
            {
                "text": f"""
⚠️ Вы уверены, что хотите вернуть средства за подписку?
Подписка:
    user_id: {subscription.user_id}

    status: {subscription.status}
    period: {subscription.period}

    amount: {subscription.amount} {subscription.currency}
    payment_method: {subscription.payment_method}

    created_at: {subscription.created_at.strftime('%d.%m.%Y')}
    {subscription.start_date.strftime('%d.%m.%Y')}-{subscription.end_date.strftime('%d.%m.%Y')}
                """,
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🚫 Нет",
                                callback_data="admin:subscriptions:refund:cancel_action",
                            ),
                            InlineKeyboardButton(
                                text="✅ Да",
                                callback_data=f"1|admin:subscriptions:{subscription.id}:refund:create",
                            ),
                        ],
                    ],
                ),
            },
        ])

        return self.plan
