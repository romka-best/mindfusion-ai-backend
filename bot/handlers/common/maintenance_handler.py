from aiogram import F, Router
from aiogram.filters import MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.locales.main import get_localization, get_user_language

maintenance_router = Router()
maintenance_router.message.filter(MagicData(F.maintenance_mode.is_(True)))
maintenance_router.callback_query.filter(MagicData(F.maintenance_mode.is_(True)))


@maintenance_router.message()
async def handle_maintenance_message(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    await message.answer(
        get_localization(user_language_code).MAINTENANCE_MODE,
    )


@maintenance_router.callback_query()
async def handle_maintenance_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    await callback.answer(
        text=get_localization(user_language_code).MAINTENANCE_MODE,
        show_alert=True,
    )
