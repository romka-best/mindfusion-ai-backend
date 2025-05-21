from aiogram.types import InlineKeyboardButton

from bot.database.models.product import ProductType
from bot.database.operations.product.getters import get_products
from bot.database.operations.product.updaters import update_product
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.admin.products import bulk_discount
from bot.keyboards.admin.products.packages.index import Index as PackagesIndex
from bot.keyboards.admin.products.subscriptions.index import Index as SubscriptionsIndex
from bot.states.admin.bulk_discount import BulkDiscountState


class BulkDiscountHandler(BaseHandler):
    async def bulk_discount(self):
        """
        Toggles bulk discount mode

        Callback:
        admin:products:bulk_discount

        When entering the mode
        - All product's btns behave like checkbox with prefix ❌ or ✅
        - The product's btns callback has the format admin:products:{product_id}:bulk_discount:toggle
        - New btn "✏️ Задать скидку" added as the second to last btn
        - Exiting the mode is performed by pressing "⚙️ Массовая скидка" again

        When exiting the mode
        - Btns revert back to normal edit mode
        - The product's btns callback has the format admin:products:{product_id}:edit
        - Btn "✏️ Задать скидку" is removed
        """
        # Determine if we're already in bulk discount mode
        is_bulk_discount_mode = any(
            btn.text == "✏️ Задать скидку" for [btn] in self.message.reply_markup.inline_keyboard
        )

        if not is_bulk_discount_mode:
            product_type = ProductType.PACKAGE if self.message.text == "Пакеты" else ProductType.SUBSCRIPTION
            products = await get_products(is_active=True, product_type=product_type)

            product_discount_map = {p.id: p.discount for p in products}

            # Update btns to show discount and toggle mode
            for [btn] in self.message.reply_markup.inline_keyboard:
                if btn.callback_data.endswith("edit"):
                    parts = btn.callback_data.split(":")
                    product_id = parts[2]

                    discount_value = product_discount_map[product_id]
                    btn.text = f"❌ {discount_value}% {btn.text}"
                    btn.callback_data = ":".join(parts[:3] + ["bulk_discount:toggle"])

            self.message.reply_markup.inline_keyboard.insert(
                -1,
                [
                    InlineKeyboardButton(
                        text="✏️ Задать скидку",
                        callback_data="admin:products:bulk_discount:ask_value",
                    ),
                ],
            )
        else:
            # Exit bulk discount mode: revert btns to normal edit mode
            for [btn] in self.message.reply_markup.inline_keyboard:
                if btn.callback_data.endswith("bulk_discount:toggle"):
                    btn.text = btn.text.rpartition("% ")[-1]  # Remove ❌ and discount number
                    btn.callback_data = ":".join(btn.callback_data.split(":")[:3] + ["edit"])

            # Remove the "Задать скидку" btn
            self.message.reply_markup.inline_keyboard = [
                row
                for row in self.message.reply_markup.inline_keyboard
                if not row or row[0].text != "✏️ Задать скидку"
            ]

        await self.message.edit_reply_markup(reply_markup=self.message.reply_markup)

    async def bulk_discount_toggle(self, product_id):
        """
        Callback:
        admin:products:{product_id}:bulk_discount:toggle
        """
        product_to_toggle = next(
            inline_btn
            for [inline_btn] in self.message.reply_markup.inline_keyboard
            if inline_btn.callback_data.split(":")[2] == product_id
        )

        if product_to_toggle.text.startswith("✅"):
            product_to_toggle.text = "❌ " + product_to_toggle.text[2:]
        else:
            product_to_toggle.text = "✅ " + product_to_toggle.text[2:]

        await self.message.edit_reply_markup(reply_markup=self.message.reply_markup)

    async def bulk_discount_ask_value(self):
        """
        Callback:
        admin:products:bulk_discout:ask_value
        """
        product_type = ProductType.PACKAGE if self.message.text == "Пакеты" else ProductType.SUBSCRIPTION

        product_ids = [
            btn.callback_data.split(":")[2]
            for [btn] in self.callback_query.message.reply_markup.inline_keyboard
            if btn.text.startswith("✅")
        ]

        await self.state.set_state(BulkDiscountState.wait_discount_value)
        await self.state.update_data(product_ids=product_ids, product_type=product_type)

        await bulk_discount.AskValue().send_render(self.message, product_type)

    async def bulk_discount_update(self, product_ids, product_type, value):
        """
        State:
        BulkDiscountState.wait_discount_value
        """
        await self.state.clear()
        self.delete_prev_msgs_num = 2
        await self._delete_prev_msgs()

        try:
            discount_value = float(value)
            if not (0 <= discount_value <= 100):
                return await self._handle_invalid_discount(product_ids, product_type)
        except (TypeError, ValueError):
            return await self._handle_invalid_discount(product_ids, product_type)

        for product_id in product_ids:
            await update_product(product_id, {"discount": discount_value})

        products = await get_products(is_active=True, product_type=product_type)
        index_class = SubscriptionsIndex if product_type == ProductType.SUBSCRIPTION else PackagesIndex

        response_msg = await self.message.answer(text="...")
        [response_msg] = await index_class().send_render(response_msg, products)
        self.message = response_msg
        await self.bulk_discount()

    async def _handle_invalid_discount(self, product_ids, product_type):
        await self.state.set_state(BulkDiscountState.wait_discount_value)
        await self.state.update_data(product_ids=product_ids, product_type=product_type)

        await self.message.answer(text="⚠️ Введите ЧИСЛО от 0 до 100")
        await bulk_discount.AskValue().send_render((await self.message.answer(text="...")), product_type)
