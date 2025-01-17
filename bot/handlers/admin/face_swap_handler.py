import asyncio
from typing import cast

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Quota
from bot.database.models.face_swap_package import FaceSwapPackageStatus, FaceSwapPackage
from bot.database.models.user import UserGender
from bot.database.operations.face_swap_package.getters import (
    get_face_swap_package,
    get_face_swap_packages_by_gender,
    get_face_swap_package_by_name_and_gender,
)
from bot.database.operations.face_swap_package.updaters import update_face_swap_package
from bot.database.operations.face_swap_package.writers import write_face_swap_package
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.writers import write_request
from bot.keyboards.admin.admin import build_admin_keyboard
from bot.locales.translate_text import translate_text
from bot.integrations.replicate_ai import create_face_swap_image
from bot.keyboards.admin.face_swap import (
    build_manage_face_swap_keyboard,
    build_manage_face_swap_create_keyboard,
    build_manage_face_swap_create_confirmation_keyboard,
    build_manage_face_swap_edit_keyboard,
    build_manage_face_swap_edit_package_change_status_keyboard,
    build_manage_face_swap_edit_choose_gender_keyboard,
    build_manage_face_swap_edit_picture_keyboard,
    build_manage_face_swap_edit_picture_change_status_keyboard,
    build_manage_face_swap_edit_choose_package_keyboard,
)
from bot.keyboards.common.common import build_cancel_keyboard
from bot.locales.main import get_localization, localization_classes, get_user_language
from bot.locales.types import LanguageCode
from bot.states.ai.face_swap import FaceSwap

admin_face_swap_router = Router()


async def handle_manage_face_swap(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(str(user_id), state.storage)

    await message.edit_text(
        text=get_localization(user_language_code).ADMIN_FACE_SWAP_INFO,
        reply_markup=build_manage_face_swap_keyboard(user_language_code),
    )


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm:'))
async def handle_face_swap_manage_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

    action = callback_query.data.split(':')[1]
    if action == 'back':
        reply_markup = build_admin_keyboard(user_language_code)
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_INFO,
            reply_markup=reply_markup,
        )

        return
    elif action == 'create':
        reply_markup = build_manage_face_swap_create_keyboard(user_language_code)
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_FACE_SWAP_CREATE,
            reply_markup=reply_markup,
        )

        await state.set_state(FaceSwap.waiting_for_face_swap_system_package_name)
    elif action == 'edit':
        reply_markup = build_manage_face_swap_edit_choose_gender_keyboard(user_language_code)
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_FACE_SWAP_EDIT_CHOOSE_GENDER,
            reply_markup=reply_markup,
        )


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm_create:'))
async def handle_face_swap_manage_create_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]

    if action == 'back':
        await handle_manage_face_swap(callback_query.message, str(callback_query.from_user.id), state)

        await callback_query.message.delete()

        await state.clear()


@admin_face_swap_router.message(FaceSwap.waiting_for_face_swap_system_package_name, F.text, ~F.text.startswith('/'))
async def face_swap_manage_system_name_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(str(message.from_user.id), state.storage)

    system_face_swap_package_name = message.text.upper()
    face_swap_package_male = await get_face_swap_package_by_name_and_gender(
        system_face_swap_package_name,
        UserGender.MALE,
    )
    face_swap_package_female = await get_face_swap_package_by_name_and_gender(
        system_face_swap_package_name,
        UserGender.FEMALE,
    )
    if face_swap_package_male or face_swap_package_female:
        await message.answer(
            text=get_localization(user_language_code).ADMIN_FACE_SWAP_CREATE_PACKAGE_ALREADY_EXISTS_ERROR,
        )
    else:
        reply_markup = build_cancel_keyboard(user_language_code)
        await message.answer(
            text=get_localization(user_language_code).ADMIN_FACE_SWAP_CREATE_PACKAGE_NAME,
            reply_markup=reply_markup,
        )

        await state.update_data(system_face_swap_package_name=system_face_swap_package_name)
        await state.set_state(FaceSwap.waiting_for_face_swap_package_name)


@admin_face_swap_router.message(FaceSwap.waiting_for_face_swap_package_name, F.text, ~F.text.startswith('/'))
async def face_swap_manage_name_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(str(message.from_user.id), state.storage)
    user_data = await state.get_data()

    face_swap_package_names = {}
    for language_code in localization_classes.keys():
        if language_code == LanguageCode.RU:
            face_swap_package_names[language_code] = message.text
        else:
            translated_face_swap_package_name = await translate_text(message.text, LanguageCode.RU, language_code)
            if translated_face_swap_package_name:
                face_swap_package_names[language_code] = translated_face_swap_package_name
            else:
                face_swap_package_names[language_code] = message.text

    reply_markup = build_manage_face_swap_create_confirmation_keyboard(user_language_code)
    await message.answer(
        text=get_localization(user_language_code).admin_face_swap_create_package_confirmation(
            package_system_name=user_data['system_face_swap_package_name'],
            package_names=face_swap_package_names,
        ),
        reply_markup=reply_markup,
    )

    await state.update_data(face_swap_package_names=face_swap_package_names)


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm_create_confirmation:'))
async def handle_face_swap_manage_create_confirmation_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]

    if action == 'approve':
        user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)
        user_data = await state.get_data()

        await write_face_swap_package(
            name=user_data['system_face_swap_package_name'],
            translated_names=user_data['face_swap_package_names'],
            gender=UserGender.MALE,
            files=[],
            status=FaceSwapPackageStatus.PRIVATE,
        )
        await write_face_swap_package(
            name=user_data['system_face_swap_package_name'],
            translated_names=user_data['face_swap_package_names'],
            gender=UserGender.FEMALE,
            files=[],
            status=FaceSwapPackageStatus.PRIVATE,
        )

        answered_message = await callback_query.message.answer(
            text=get_localization(user_language_code).ADMIN_FACE_SWAP_CREATE_PACKAGE_SUCCESS)
        await handle_manage_face_swap(answered_message, str(callback_query.from_user.id), state)

        await callback_query.message.delete()
        await state.clear()


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm_edit_choose_gender:'))
async def handle_face_swap_manage_edit_choose_gender_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

    gender = cast(UserGender, callback_query.data.split(':')[1])

    face_swap_packages = await get_face_swap_packages_by_gender(gender)
    reply_markup = build_manage_face_swap_edit_choose_package_keyboard(user_language_code, face_swap_packages)
    await callback_query.message.edit_text(
        text=get_localization(user_language_code).ADMIN_FACE_SWAP_EDIT_CHOOSE_PACKAGE,
        reply_markup=reply_markup,
    )

    await state.update_data(gender=gender)


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm_edit_choose_package:'))
async def handle_face_swap_manage_edit_choose_package_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)
    user_data = await state.get_data()

    package_name = user_data.get('package_name', callback_query.data.split(':')[1])

    reply_markup = build_manage_face_swap_edit_keyboard(user_language_code)
    await callback_query.message.edit_text(
        text=get_localization(user_language_code).ADMIN_FACE_SWAP_EDIT,
        reply_markup=reply_markup,
    )

    await state.update_data(package_name=package_name)


async def show_picture(
    file: dict,
    language_code: LanguageCode,
    face_swap_package: FaceSwapPackage,
    callback_query: CallbackQuery,
):
    file_name, file_status = file.get('name'), file.get('status')
    try:
        reply_markup = build_manage_face_swap_edit_picture_keyboard(language_code, file_name)

        photo_path = f'face_swap/{face_swap_package.gender.lower()}/{face_swap_package.name.lower()}/{file_name}'
        photo = await firebase.bucket.get_blob(photo_path)
        photo_link = firebase.get_public_url(photo.name)

        await callback_query.message.answer_photo(
            photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
            caption=f'<b>{file_name}</b>\n\n{file_status}',
            reply_markup=reply_markup,
        )
    except Exception as e:
        await callback_query.message.answer(
            text=f'{file_name}\n\n{get_localization(language_code).ERROR}:\n{e}',
            parse_mode=None
        )


async def show_pictures(face_swap_package: FaceSwapPackage, language_code: LanguageCode, callback_query: CallbackQuery):
    tasks = [
        show_picture(
            file,
            language_code,
            face_swap_package,
            callback_query,
        ) for file in face_swap_package.files
    ]
    await asyncio.gather(*tasks)


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm_edit:'))
async def handle_face_swap_manage_edit_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]

    if action == 'back':
        await handle_manage_face_swap(callback_query.message, str(callback_query.from_user.id), state)

        await callback_query.message.delete()

        await state.clear()
    else:
        user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)
        user_data = await state.get_data()
        face_swap_package = await get_face_swap_package_by_name_and_gender(
            user_data['package_name'],
            user_data['gender'],
        )
        await state.update_data(face_swap_package_id=face_swap_package.id)

        if action == 'change_status':
            reply_markup = build_manage_face_swap_edit_package_change_status_keyboard(
                user_language_code,
                face_swap_package.status,
            )
            await callback_query.message.edit_text(
                text=get_localization(user_language_code).ADMIN_FACE_SWAP_CHANGE_STATUS,
                reply_markup=reply_markup
            )
        elif action == 'show_pictures':
            await show_pictures(face_swap_package, user_language_code, callback_query)
        elif action == 'add_new_picture':
            reply_markup = build_cancel_keyboard(user_language_code)
            await callback_query.message.edit_text(
                text=get_localization(user_language_code).ADMIN_FACE_SWAP_ADD_NEW_PICTURE_NAME,
                reply_markup=reply_markup,
            )
            await state.set_state(FaceSwap.waiting_for_face_swap_picture_name)


@admin_face_swap_router.message(FaceSwap.waiting_for_face_swap_picture_name, ~F.text.startswith('/'))
async def face_swap_manage_picture_name_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(str(message.from_user.id), state.storage)

    reply_markup = build_cancel_keyboard(user_language_code)
    await message.answer(
        text=get_localization(user_language_code).ADMIN_FACE_SWAP_ADD_NEW_PICTURE_IMAGE,
        reply_markup=reply_markup,
    )

    await state.update_data(face_swap_picture_name=message.text.title())
    await state.set_state(FaceSwap.waiting_for_face_swap_picture_image)


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm_edit_package_change_status:'))
async def handle_face_swap_manage_edit_package_change_status_selection(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    await callback_query.answer()

    user_data = await state.get_data()

    status = callback_query.data.split(':')[1]

    if status == 'back':
        await handle_face_swap_manage_edit_choose_package_selection(callback_query, state)
        return

    keyboard = callback_query.message.reply_markup.inline_keyboard
    keyboard_changed = False

    new_keyboard = []
    for row in keyboard:
        new_row = []
        for button in row:
            text = button.text
            callback_data = button.callback_data.split(':', 1)[1]

            if callback_data == status:
                if '✅' not in text:
                    text += ' ✅'
                    keyboard_changed = True
            else:
                text = text.replace(' ✅', '')
            new_row.append(InlineKeyboardButton(text=text, callback_data=button.callback_data))
        new_keyboard.append(new_row)

    if keyboard_changed:
        await update_face_swap_package(user_data['face_swap_package_id'], {
            'status': status
        })
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard))


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm_edit_picture:'))
async def handle_face_swap_manage_edit_picture_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)
    user_data = await state.get_data()

    action, file_name = callback_query.data.split(':')[1], callback_query.data.split(':')[2]
    face_swap_package = await get_face_swap_package(user_data['face_swap_package_id'])
    file_status = FaceSwapPackageStatus.PRIVATE
    for file in face_swap_package.files:
        if file['name'] == file_name:
            file_status = file.get('status')
            break

    if action == 'change_status':
        await callback_query.message.edit_reply_markup(
            reply_markup=build_manage_face_swap_edit_picture_change_status_keyboard(user_language_code, file_status),
        )
        await state.update_data(file_name=file_name)
    elif action == 'example_picture':
        processing_sticker = await callback_query.message.answer_sticker(
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
        )
        processing_message = await callback_query.message.reply(
            text=get_localization(user_language_code).model_face_swap_processing_request(),
            allow_sending_without_reply=True,
        )

        async with ChatActionSender.upload_photo(
            bot=callback_query.message.bot,
            chat_id=callback_query.message.chat.id,
        ):
            user_photo_blobs = await firebase.bucket.list_blobs(prefix=f'users/avatars/{user_id}.')
            user_photo = await firebase.bucket.get_blob(user_photo_blobs[-1])
            user_photo_link = firebase.get_public_url(user_photo.name)

            image_path = f'face_swap/{face_swap_package.gender.lower()}/{face_swap_package.name.lower()}/{file_name}'
            image = await firebase.bucket.get_blob(image_path)
            image_link = firebase.get_public_url(image.name)

            product = await get_product_by_quota(Quota.FACE_SWAP)

            request = await write_request(
                user_id=user_id,
                processing_message_ids=[processing_sticker.message_id, processing_message.message_id],
                product_id=product.id,
                requested=1,
                details={
                    'is_test': True,
                    'face_swap_package_id': face_swap_package.id,
                    'face_swap_package_name': face_swap_package.name,
                },
            )

            face_swap_response = await create_face_swap_image(image_link, user_photo_link)
            await write_generation(
                id=face_swap_response,
                request_id=request.id,
                product_id=product.id,
                has_error=face_swap_response is None,
            )


@admin_face_swap_router.callback_query(lambda c: c.data.startswith('fsm_edit_picture_change_status:'))
async def handle_face_swap_manage_edit_picture_change_status_selection(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    await callback_query.answer()

    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)
    user_data = await state.get_data()

    status = cast(FaceSwapPackageStatus, callback_query.data.split(':')[1])
    if status == 'back':
        await callback_query.message.edit_reply_markup(
            reply_markup=build_manage_face_swap_edit_picture_keyboard(user_language_code, user_data['file_name'])
        )
        return

    face_swap_package = await get_face_swap_package(user_data['face_swap_package_id'])
    for file in face_swap_package.files:
        if file['name'] == user_data['file_name']:
            file['status'] = status
            break

    keyboard = callback_query.message.reply_markup.inline_keyboard
    keyboard_changed = False

    new_keyboard = []
    for row in keyboard:
        new_row = []
        for button in row:
            text = button.text
            callback_data = button.callback_data.split(':', 1)[1]

            if callback_data == status:
                if '✅' not in text:
                    text += ' ✅'
                    keyboard_changed = True
            else:
                text = text.replace(' ✅', '')
            new_row.append(InlineKeyboardButton(text=text, callback_data=button.callback_data))
        new_keyboard.append(new_row)

    if keyboard_changed:
        await update_face_swap_package(user_data['face_swap_package_id'], {
            'files': face_swap_package.files
        })
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard))
