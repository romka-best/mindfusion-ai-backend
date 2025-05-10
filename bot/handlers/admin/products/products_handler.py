from bot.database.operations.product.getters import get_product
from bot.database.operations.product.updaters import update_product
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.admin.admin import build_admin_keyboard
from bot.keyboards.admin.products.ask_new_field_value import AskNewFieldValue
from bot.keyboards.admin.products.edit import Edit
from bot.keyboards.admin.products.edit_desc import EditDesc
from bot.keyboards.admin.products.edit_name import EditName
from bot.keyboards.admin.products.edit_price import EditPrice
from bot.keyboards.admin.products.select_type import SelectType
from bot.locales.main import get_localization
from bot.states.admin.products import Products
from bot.utils.is_admin import is_admin


class ProductsHandler(BaseHandler):
    async def edit(self, product_id, field=None):
        """
        Callback:
        admin:products:{product_id}:edit:?{field}
        """
        product = await get_product(product_id)

        match field:
            case "desc":
                await EditDesc().send_render(self.message, product)
            case "name":
                await EditName().send_render(self.message, product)
            case "price":
                await EditPrice().send_render(self.message, product)
            case "discount":
                await self._ask_new_field_value(field, product.discount, product_id)
            case _:
                await Edit().send_render(self.message, product)

    async def update(self, product_id, field_name, value, original_message_id):
        """
        State:
        Products.waiting_edit_new_value
        """
        product = await get_product(product_id)
        await self.state.clear()

        product = await get_product(product_id)

        match field_name:
            case str() as field if field.startswith("desc"):
                _, lang = field.split("_")
                product.descriptions.update({lang: value})
                new_data = {"descriptions": product.descriptions}
            case str() as field if field.startswith("name"):
                _, lang = field.split("_")
                product.names.update({lang: value})
                new_data = {"names": product.names}
            case str() as field if field.startswith("price"):
                _, currency = field.split("_")
                product.prices.update({
                    currency: float(value),
                })  # TODO Use decimal for money, codebase needs refactoring
                new_data = {"prices": product.prices}
            case "discount":
                product.discount = int(value)
                new_data = {field_name: int(value)}

        await update_product(product_id, new_data)

        await self.message.delete()
        await self.message.bot.edit_message_text(
            chat_id=self.message.chat.id, message_id=original_message_id, **Edit().render(product)[0][1],
        )

    async def back_to_admin(self):
        """
        Callback:
        admin:products:back_to_admin
        """
        await self.state.clear()

        if not is_admin(str(self.user_id)):
            return

        await self.message.edit_text(
            text=get_localization(self.lang_code).ADMIN_INFO,
            reply_markup=build_admin_keyboard(self.lang_code),
        )

    async def select_type(self):
        """
        Callback:
        admin:products:select_type
        """
        await SelectType().send_render(self.message)

    async def cancel_edit(self, product_id):
        """
        Callback:
        admin:products:cancel_edit
        """
        product = await get_product(product_id)

        await Edit().send_render(self.message, product)

    async def cancel_update(self):
        """
        Callback:
        admin:products:cancel_update
        """
        data = await self.state.get_data()
        product = await get_product(data["product_id"])
        self.state.clear()

        await Edit().send_render(self.message, product)

    async def ask_new_field_value(self, product_id, field_name):
        """
        Callback:
        admin:products:{product_id}:anfv:{field_name}
        """
        product = await get_product(product_id)

        old_value = ""

        match field_name:
            case str() as field if field.startswith("desc"):
                _, lang = field.split("_")
                old_value = product.descriptions[lang]
            case str() as field if field.startswith("name"):
                _, lang = field.split("_")
                old_value = product.names[lang]
            case str() as field if field.startswith("price"):
                _, currency = field.split("_")
                old_value = product.prices[currency]

        await self._ask_new_field_value(field_name, old_value, product_id)

    async def _ask_new_field_value(self, field_name, old_value, product_id):
        msgs = await AskNewFieldValue().send_render(self.message, old_value)

        await self.state.set_state(Products.waiting_edit_new_value)
        await self.state.update_data(
            product_id=product_id,
            field_name=field_name,
            original_message_id=msgs[0].message_id,
        )
