import re

from aiogram import Router

from bot.database.main import firebase
from bot.database.models.common import Model
from bot.database.models.user import User
from bot.database.operations.user.getters import get_user
from bot.helpers.gpt_image.user.settings.settings import Settings
from bot.keyboards.ai.openai.gpt_image.settings.edit import Edit
from bot.locales.main import get_user_language


class SettingsHandler:
    async def edit(self, callback_query, state):
        """
        Callback:
        oai:gpt-image:settings:edit
        """
        user_id = str(callback_query.from_user.id)
        user = await get_user(user_id)
        lang_code = await get_user_language(user_id, state.storage)

        message_args = Edit().render(lang_code, **user.settings[Model.GPT_IMAGE])
        await callback_query.message.edit_text(**message_args)

    async def update(self, callback_query):
        """
        Callback:
        oai:gpt-image:settings:update:{field_name}:{value}
        """
        user_id = str(callback_query.from_user.id)
        _, _, _, _, field_name, value = callback_query.data.split(":")

        # Update field in db
        user_ref = firebase.db.collection(User.COLLECTION_NAME).document(user_id)
        await user_ref.update({
            f"settings.{Model.GPT_IMAGE}.{field_name}": Settings[field_name.upper()].value[value].value,
        })

        # Ticking checkbox for new setting
        tick_btn = next(
            btn
            for row in callback_query.message.reply_markup.inline_keyboard
            for btn in row
            if btn.callback_data == callback_query.data
        )

        untick_btn = next(
            btn
            for row in callback_query.message.reply_markup.inline_keyboard
            for btn in row
            if btn.callback_data.startswith(":".join(callback_query.data.split(":")[:5])) and btn.text[0] == "✅"
        )

        # It's important to untick first, then tick
        # Since untick_btn and tick_btn can be same
        # Because of this, setting may be in invalide state, where no one option is active
        untick_btn.text = "❌" + untick_btn.text[1:]
        tick_btn.text = "✅" + tick_btn.text[1:]

        await callback_query.message.edit_reply_markup(reply_markup=callback_query.message.reply_markup)


r = Router()
r.callback_query(lambda c: c.data == "oai:gpt-image:settings:edit")(SettingsHandler().edit)
r.callback_query(lambda c: re.match(r"^oai:gpt-image:settings:update:(.+)$", c.data))(SettingsHandler().update)
settings_router = r
