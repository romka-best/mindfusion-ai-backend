from typing import cast

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.database.operations.user.getters import get_user
from bot.helpers.setters.set_commands import set_commands_for_user
from bot.keyboards.settings.language import build_language_keyboard
from bot.locales.main import get_localization, get_user_language, set_user_language
from bot.locales.types import LanguageCode
from bot.utils.is_admin import is_admin
from bot.utils.is_developer import is_developer

language_router = Router()


@language_router.message(Command('language'))
async def language(message: Message, state: FSMContext):
    await state.clear()

    user_language_code = await get_user_language(str(message.from_user.id), state.storage)

    await message.answer(
        text=get_localization(user_language_code).LANGUAGE,
        reply_markup=build_language_keyboard(user_language_code),
    )


@language_router.callback_query(lambda c: c.data.startswith('language:'))
async def handle_language_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(str(callback_query.from_user.id))

    chosen_language = cast(LanguageCode, callback_query.data.split(':')[1])
    await set_user_language(user_id, chosen_language, state.storage)

    if not is_admin(str(callback_query.message.chat.id)) and not is_developer(str(callback_query.message.chat.id)):
        await set_commands_for_user(callback_query.bot, user.telegram_chat_id, chosen_language)

    await callback_query.message.answer(
        text=get_localization(chosen_language).LANGUAGE_CHOSEN,
    )

    await callback_query.message.delete()
