import logging
from datetime import datetime, timezone
from decimal import Decimal

from google.cloud import firestore

from bot.database.main import firebase
from bot.database.models.common import PaymentMethod
from bot.database.models.product import ProductType
from bot.database.models.subscription import Subscription, SubscriptionStatus
from bot.database.models.transaction import Transaction
from bot.database.operations.product.getters import get_products
from bot.database.operations.subscription.getters import get_subscription, get_user_refaundable_subscriptions_by_user_id
from bot.database.operations.transaction.getters import get_transaction_by_subscription_id
from bot.database.operations.user.getters import get_user
from bot.handlers.base_handler import BaseHandler
from bot.helpers.billing.refund.providers.stripe_refund import StripeRefund
from bot.helpers.billing.refund.providers.telegram_stars_refund import TelegramStarsRefund
from bot.helpers.billing.refund.providers.yookassa_refund import YookassaRefund
from bot.helpers.billing.refund.refund_service import RefundService
from bot.keyboards.admin.products.subscriptions.index import Index as SubscriptionsIndex
from bot.keyboards.admin.products.subscriptions.refund.confirm import Confirm
from bot.keyboards.admin.products.subscriptions.refund.new import New
from bot.keyboards.admin.products.subscriptions.refund.show_user_subscriptions import ShowUserSubscriptions
from bot.keyboards.admin.products.subscriptions.refund.user_not_founded import UserNotFounded
from bot.states.admin.subscriptions_refund import SubscriptionsRefundState


class RefundHandler(BaseHandler):
    async def new(self):
        """
        Callback:
        admin:subscriptions:refund:new
        """
        await self.state.set_state(SubscriptionsRefundState.wait_user_id)
        await New().send_render(self.message)

    async def create(self, subscription_id: str):
        """
        Callback:
        admin:subscriptions:{subscription_id}:refund:create
        """
        subscription = await get_subscription(subscription_id)
        transaction_doc = await get_transaction_by_subscription_id(subscription_id)
        context_info_text = f"""
Provider: {subscription.payment_method}
Subscription ID: {subscription.id}
Charge ID: {subscription.provider_payment_charge_id}
Transaction ID: {transaction_doc.id}
"""

        try:
            refund_result = await RefundService({
                PaymentMethod.YOOKASSA: YookassaRefund(),
                PaymentMethod.STRIPE: StripeRefund(),
                PaymentMethod.TELEGRAM_STARS: TelegramStarsRefund(self.message.bot, subscription.user_id),
            }).execute(
                subscription.payment_method,
                subscription.provider_payment_charge_id,
                amount=Decimal(subscription.amount),
                currency=subscription.currency,
            )


            if not refund_result.success:
                await self.message.answer(f"⚠️ Ошибка возврата\n{context_info_text}")
                return

            transaction_db = firebase.db.transaction()
            await firestore.async_transactional(self._reflect_refund_in_db)(
                transaction_db,
                subscription_id,
                transaction_doc.id,
            )

            await self.message.answer(f"""
✅ Успешный возврат средств: {subscription.amount} {subscription.currency}
{context_info_text}
Refund ID: {refund_result.refund_id}
""")

        except Exception as e:
            logging.error(e, exc_info=True)  # noqa: G201, LOG015
            await self.message.answer(f"⚠️ Произошла ошибка\n{context_info_text}\n{e}")

    async def show_user_subscriptions(self, user_id):
        """
        State
        SubscriptionsRefundState.wait_user_id
        """
        await self.state.clear()
        self.delete_prev_msgs_num = 2
        await self._delete_prev_msgs()

        user = await get_user(user_id)

        if not user:
            return await UserNotFounded().send_render(self.message, user_id)

        subscriptions = await get_user_refaundable_subscriptions_by_user_id(user.id)

        await ShowUserSubscriptions().send_render(self.message, user, subscriptions)

    async def confirm(self, subscription_id):
        subscription = await get_subscription(subscription_id)

        await Confirm().send_render(self.message, subscription)

    async def cancel_action(self):
        """
        Callback:
        admin:subscriptions:refund:cancel_action
        """
        await self.state.clear()

        products = await get_products(is_active=True, product_type=ProductType.SUBSCRIPTION)
        await SubscriptionsIndex().send_render(self.message, products)

    async def _reflect_refund_in_db(self, transaction, subscription_id, transaction_doc_id):
        now = datetime.now(timezone.utc)

        transaction_ref = firebase.db.collection(Transaction.COLLECTION_NAME).document(transaction_doc_id)
        subscription_ref = firebase.db.collection(Subscription.COLLECTION_NAME).document(subscription_id)

        transaction.update(
            transaction_ref,
            {
                "amount": 0,
                "clear_amount": 0,
                "edited_at": now,
            },
        )
        transaction.update(
            subscription_ref,
            {
                "status": SubscriptionStatus.FINISHED,
                "income_amount": 0,
                "end_date": now,
                "edited_at": now,
            },
        )
