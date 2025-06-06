from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.handlers.admin.ads_handler import handle_ads
from bot.handlers.admin.ban_handler import handle_ban
from bot.handlers.admin.blast_handler import handle_blast
from bot.handlers.admin.catalog_handler import handle_manage_catalog
from bot.handlers.admin.face_swap_handler import handle_manage_face_swap
from bot.handlers.admin.promo_code_handler import handle_create_promo_code
from bot.handlers.admin.statistics_handler import handle_statistics
from bot.keyboards.admin.admin import build_admin_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.utils.is_admin import is_admin
from .products.products_router import products_router, admin_products_resolver
from bot.utils.with_user_language import with_user_language


admin_router = Router()
admin_router.include_router(products_router)

@admin_router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    await state.clear()

    if is_admin(str(message.chat.id)):
        user_language_code = await get_user_language(str(message.chat.id), state.storage)

        await message.answer(
            text=get_localization(user_language_code).ADMIN_INFO,
            reply_markup=build_admin_keyboard(user_language_code),
        )


@admin_router.callback_query(lambda c: c.data.startswith('admin:'))
@with_user_language
async def handle_admin_selection(callback_query: CallbackQuery, state: FSMContext, lang_code, user_id, delete_prev_msgs_num=0):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]
    if action == 'create_promo_code':
        await handle_create_promo_code(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'manage_face_swap':
        await handle_manage_face_swap(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'manage_catalog':
        await handle_manage_catalog(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'statistics':
        await handle_statistics(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'ads':
        await handle_ads(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'blast':
        await handle_blast(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'ban':
        await handle_ban(callback_query.message, str(callback_query.from_user.id), state)
    elif action in ("products", "packages", "subscriptions"):
        await admin_products_resolver(callback_query, state, lang_code, user_id, delete_prev_msgs_num)



@admin_router.callback_query(lambda c: c.data.startswith('developer:'))
async def handle_developer_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]
    if action == 'manage_face_swap':
        await handle_manage_face_swap(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'manage_catalog':
        await handle_manage_catalog(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'statistics':
        await handle_statistics(callback_query.message, str(callback_query.from_user.id), state)
