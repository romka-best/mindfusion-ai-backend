import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.helpers.senders.send_message_to_users import send_message_to_users
from bot.keyboards.admin.admin import build_admin_keyboard
from bot.locales.translate_text import translate_text
from bot.keyboards.admin.blast import (
    build_blast_keyboard,
    build_blast_language_keyboard,
    build_blast_confirmation_keyboard,
)
from bot.keyboards.common.common import build_cancel_keyboard
from bot.locales.main import get_localization, localization_classes, get_user_language
from bot.locales.types import LanguageCode
from bot.states.admin.blast import Blast

blast_router = Router()


async def handle_blast(message: Message, user_id: str, state: FSMContext):
    await state.clear()

    user_language_code = await get_user_language(user_id, state.storage)

    await message.edit_text(
        text=get_localization(user_language_code).ADMIN_BLAST_CHOOSE_USER_TYPE,
        reply_markup=build_blast_keyboard(user_language_code),
    )


@blast_router.callback_query(lambda c: c.data.startswith('blast:'))
async def handle_blast_user_type_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

    user_type = callback_query.data.split(':')[1]
    if user_type == 'back':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_INFO,
            reply_markup=build_admin_keyboard(user_language_code),
        )

        return
    else:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_BLAST_CHOOSE_USER_TYPE,
            reply_markup=build_blast_language_keyboard(user_language_code),
        )

        await state.update_data(blast_user_type=user_type)


@blast_router.callback_query(lambda c: c.data.startswith('blast_language:'))
async def handle_blast_language_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

    language = callback_query.data.split(':')[1]
    reply_markup = build_cancel_keyboard(user_language_code)
    if language == 'back':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_INFO,
            reply_markup=build_admin_keyboard(user_language_code),
        )

        return
    elif language == 'all':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_BLAST_WRITE_IN_DEFAULT_LANGUAGE,
            reply_markup=reply_markup,
        )
    else:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_BLAST_WRITE_IN_CHOSEN_LANGUAGE,
            reply_markup=reply_markup,
        )

    await state.set_state(Blast.waiting_for_blast_letter)
    await state.update_data(blast_language=language)


@blast_router.message(Blast.waiting_for_blast_letter, F.text, ~F.text.startswith('/'))
async def blast_letter_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(str(message.from_user.id), state.storage)
    user_data = await state.get_data()

    blast_letters = {}
    blast_language = user_data['blast_language']
    if blast_language != 'all':
        blast_letters[blast_language] = message.text
    else:
        for language_code in localization_classes.keys():
            if language_code == LanguageCode.RU:
                blast_letters[language_code] = message.text
            else:
                translated_blast_letter = await translate_text(message.text, LanguageCode.RU, language_code)
                if translated_blast_letter:
                    blast_letters[language_code] = translated_blast_letter
                else:
                    blast_letters[language_code] = message.text

    await message.answer(
        text=get_localization(user_language_code).admin_blast_confirmation(blast_letters),
        reply_markup=build_blast_confirmation_keyboard(user_language_code),
    )

    await state.update_data(blast_letters=blast_letters)


@blast_router.callback_query(lambda c: c.data.startswith('blast_confirmation:'))
async def handle_blast_confirmation_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]

    if action == 'approve':
        user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)
        user_data = await state.get_data()

        blast_user_type = user_data['blast_user_type']
        blast_language = user_data['blast_language']
        blast_letters = user_data['blast_letters']

        tasks = []
        if blast_language == 'all':
            for language_code in localization_classes.keys():
                tasks.append(
                    send_message_to_users(
                        bot=callback_query.bot,
                        user_type=blast_user_type,
                        language_code=language_code,
                        message=blast_letters[language_code],
                    )
                )
        else:
            tasks.append(
                send_message_to_users(
                    bot=callback_query.bot,
                    user_type=blast_user_type,
                    language_code=blast_language,
                    message=blast_letters[blast_language],
                )
            )
        await asyncio.gather(*tasks, return_exceptions=True)

        await callback_query.message.answer(text=get_localization(user_language_code).ADMIN_BLAST_SUCCESS)
        await callback_query.message.delete()

        await state.clear()
