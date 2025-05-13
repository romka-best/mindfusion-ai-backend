from aiogram import Router

from bot import keyboards
from bot.database.models.common import Quota
from bot.database.operations.user.getters import get_user
from bot.handlers.ai.model_handler import handle_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.locales.main import get_user_language

from .settings_handler import settings_router


class GptImageHandler:
    async def show(self, callback_query, state):
        user_id = str(callback_query.from_user.id)
        user = await get_user(user_id)
        lang_code = await get_user_language(user_id, state.storage)

        text = await get_switched_to_ai_model(user, Quota.GPT_IMAGE, lang_code)
        reply_markup = keyboards.ai.openai.gpt_image.Show().render(lang_code)

        await callback_query.message.edit_text(text=text, reply_markup=reply_markup)

    async def back_to_models(self, callback_query, state):
        await handle_model(callback_query.message, str(callback_query.from_user.id), state, is_edit=True, page=2)


r = Router()
r.include_routers(settings_router)
r.callback_query(lambda c: c.data == "oai:gpt-image:show")(GptImageHandler().show)
r.callback_query(lambda c: c.data == "oai:gpt-image:back_to_models")(GptImageHandler().back_to_models)

gpt_image_router = r
