from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.common import Currency
from bot.keyboards.base_view import BaseView


class ShowUserSubscriptions(BaseView):
    def render(self, user, subscriptions):
        self.plan_add([
            "answer",
            {
                "text": f"""
Пользователь:
    id: {user.id}
    username: {user.username}
    first_name: {user.first_name}
    last_name: {user.last_name}
    language_code: {user.language_code}
    is_banned: {user.is_banned}

    currency: {Currency.SYMBOLS[user.currency]}
    had_subscription: {user.had_subscription}
    stripe_id: {user.stripe_id}
    subscription_id: {user.subscription_id}
                """,
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=f"{Currency.SYMBOLS[sub.currency]}{sub.amount} {sub.start_date.strftime('%d.%m.%Y')}-{sub.end_date.strftime('%d.%m.%Y')} {sub.status}",
                                callback_data=f"admin:subscriptions:{sub.id}:refund:confirm",
                            ),
                        ]
                        for sub in subscriptions
                    ],
                ),
            },
        ])

        return self.plan
