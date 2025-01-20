from typing import Optional, cast

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    URLInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from bot.database.main import firebase
from bot.database.models.common import Model, Quota, ModelType
from bot.database.operations.chat.getters import get_chat_by_user_id
from bot.database.operations.chat.updaters import update_chat
from bot.database.operations.product.getters import get_product
from bot.database.operations.prompt.getters import (
    get_prompt_categories_by_model_type,
    get_prompt_subcategories_by_category_id,
    get_prompts_by_subcategory_id,
    get_prompt,
)
from bot.database.operations.role.getters import get_roles, get_role
from bot.database.operations.user.getters import get_user
from bot.helpers.getters.get_human_model import get_human_model
from bot.helpers.getters.get_model_type import get_model_type
from bot.keyboards.common.common import build_buy_motivation_keyboard
from bot.keyboards.settings.catalog import (
    build_catalog_keyboard,
    build_catalog_digital_employees_keyboard,
    build_catalog_prompts_model_type_keyboard,
    build_catalog_prompt_categories_keyboard,
    build_catalog_prompt_subcategories_keyboard,
    build_prompts_catalog_keyboard,
    build_prompts_catalog_chosen_keyboard,
    build_prompts_catalog_copy_keyboard,
)
from bot.keyboards.settings.settings import build_settings_keyboard, build_settings_choose_text_model_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode

catalog_router = Router()


@catalog_router.message(Command('catalog'))
async def catalog(message: Message, state: FSMContext):
    await state.clear()

    user_language_code = await get_user_language(str(message.from_user.id), state.storage)

    await message.answer(
        text=get_localization(user_language_code).CATALOG_INFO,
        reply_markup=build_catalog_keyboard(user_language_code),
    )


@catalog_router.callback_query(lambda c: c.data.startswith('catalog:'))
async def handle_catalog_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]
    if action == 'digital_employees':
        await handle_catalog_digital_employees(
            callback_query.message,
            str(callback_query.from_user.id),
            state,
        )
    elif action == 'prompts':
        await handle_catalog_prompts(
            callback_query.message,
            str(callback_query.from_user.id),
            state,
        )


async def handle_catalog_digital_employees(
    message: Message,
    user_id: str,
    state: FSMContext,
    model: Optional[Model] = None,
    from_settings=False,
):
    user_language_code = await get_user_language(user_id, state.storage)

    current_chat = await get_chat_by_user_id(user_id)
    roles = await get_roles()

    await message.edit_text(
        text=get_localization(user_language_code).CATALOG_DIGITAL_EMPLOYEES_INFO,
        reply_markup=build_catalog_digital_employees_keyboard(
            user_language_code,
            current_chat.role_id,
            roles,
            model,
            from_settings,
        ),
    )


@catalog_router.callback_query(lambda c: c.data.startswith('catalog_digital_employees:'))
async def handle_catalog_digital_employees_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    role_id = callback_query.data.split(':')[1]
    if role_id == 'back':
        from_settings = callback_query.data.split(':')[2] == 'True'
        if from_settings:
            if len(callback_query.data.split(':')) == 4:
                chosen_model = cast(Model, callback_query.data.split(':')[-1])
                human_model = get_human_model(chosen_model, user_language_code)
                await callback_query.message.edit_text(
                    text=get_localization(user_language_code).settings_info(human_model, chosen_model),
                    reply_markup=build_settings_keyboard(
                        language_code=user_language_code,
                        model=chosen_model,
                        model_type=get_model_type(chosen_model),
                        settings=user.settings,
                    ),
                )
            else:
                await callback_query.message.edit_text(
                    text=get_localization(user_language_code).SETTINGS_CHOOSE_MODEL,
                    reply_markup=build_settings_choose_text_model_keyboard(user_language_code),
                )
        else:
            await callback_query.message.edit_text(
                text=get_localization(user_language_code).CATALOG_INFO,
                reply_markup=build_catalog_keyboard(user_language_code),
            )
        return

    role = await get_role(role_id)

    role_photo = await firebase.bucket.get_blob(role.photo)
    role_photo_link = firebase.get_public_url(role_photo.name)

    if not user.daily_limits[Quota.ACCESS_TO_CATALOG] and not user.additional_usage_quota[Quota.ACCESS_TO_CATALOG]:
        await callback_query.message.reply_photo(
            photo=URLInputFile(role_photo_link, filename=role.photo, timeout=300),
            caption=get_localization(user_language_code).CATALOG_DIGITAL_EMPLOYEES_FORBIDDEN_ERROR,
            reply_markup=build_buy_motivation_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )
    else:
        keyboard = callback_query.message.reply_markup.inline_keyboard
        keyboard_changed = False

        new_keyboard = []
        for row in keyboard:
            new_row = []
            for button in row:
                text = button.text
                callback_data = button.callback_data.split(':', 1)[1]

                if callback_data == role_id:
                    if '❌' in text:
                        text = text.replace(' ❌', ' ✅')
                        keyboard_changed = True
                else:
                    text = text.replace(' ✅', ' ❌')
                new_row.append(InlineKeyboardButton(text=text, callback_data=button.callback_data))
            new_keyboard.append(new_row)

        if keyboard_changed:
            current_chat = await get_chat_by_user_id(user_id)
            await update_chat(current_chat.id, {
                'role_id': role_id,
            })

            await callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard),
            )

            await callback_query.message.reply_photo(
                photo=URLInputFile(role_photo_link, filename=role.photo, timeout=300),
                caption=role.translated_descriptions.get(user_language_code) or
                        role.translated_descriptions.get(LanguageCode.EN),
                allow_sending_without_reply=True,
            )


async def handle_catalog_prompts(
    message: Message,
    user_id: str,
    state: FSMContext,
    is_edit=True,
):
    user_language_code = await get_user_language(user_id, state.storage)

    text = get_localization(user_language_code).CATALOG_PROMPTS_CHOOSE_MODEL_TYPE
    reply_markup = build_catalog_prompts_model_type_keyboard(user_language_code)
    if is_edit:
        await message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )
    else:
        await message.answer(
            text=text,
            reply_markup=reply_markup,
        )


@catalog_router.callback_query(lambda c: c.data.startswith('catalog_prompts_model_type:'))
async def handle_catalog_prompts_model_type_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    model_type = cast(ModelType, callback_query.data.split(':')[1])
    if model_type == 'back':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).CATALOG_INFO,
            reply_markup=build_catalog_keyboard(user_language_code),
        )
    else:
        await state.update_data(prompt_model_type=model_type)
        await handle_catalog_prompts_model_type(
            callback_query.message,
            user_id,
            state,
        )


async def handle_catalog_prompts_model_type(message: Message, user_id: str, state: FSMContext, is_edit=True):
    user_language_code = await get_user_language(user_id, state.storage)
    user_data = await state.get_data()

    prompt_categories = await get_prompt_categories_by_model_type(user_data.get('prompt_model_type'))

    text = get_localization(user_language_code).CATALOG_PROMPTS_CHOOSE_CATEGORY
    reply_markup = build_catalog_prompt_categories_keyboard(
        user_language_code,
        prompt_categories,
        user_data.get('prompt_has_close_button', False),
    )
    if is_edit:
        await message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )
    else:
        await message.answer(
            text=text,
            reply_markup=reply_markup,
        )


@catalog_router.callback_query(lambda c: c.data.startswith('catalog_prompt_category:'))
async def handle_catalog_prompts_category_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    category_id = callback_query.data.split(':')[1]
    if category_id == 'back':
        await handle_catalog_prompts(
            callback_query.message,
            user_id,
            state,
        )
    else:
        await state.update_data(prompt_category_id=category_id)
        await handle_catalog_prompts_category(
            callback_query.message,
            user_id,
            state,
        )


async def handle_catalog_prompts_category(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(user_id, state.storage)
    user_data = await state.get_data()

    prompt_subcategories = await get_prompt_subcategories_by_category_id(user_data.get('prompt_category_id'))

    await message.edit_text(
        text=get_localization(user_language_code).CATALOG_PROMPTS_CHOOSE_SUBCATEGORY,
        reply_markup=build_catalog_prompt_subcategories_keyboard(user_language_code, prompt_subcategories),
    )


@catalog_router.callback_query(lambda c: c.data.startswith('catalog_prompt_subcategory:'))
async def handle_catalog_prompts_subcategory_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    subcategory_id = callback_query.data.split(':')[1]
    if subcategory_id == 'back':
        await handle_catalog_prompts_model_type(
            callback_query.message,
            user_id,
            state,
        )
    else:
        await state.update_data(prompt_subcategory_id=subcategory_id)
        await handle_catalog_prompts_subcategory(
            callback_query.message,
            user_id,
            state,
        )


async def handle_catalog_prompts_subcategory(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(user_id, state.storage)
    user_data = await state.get_data()

    prompts = await get_prompts_by_subcategory_id(user_data.get('prompt_subcategory_id'))

    await message.edit_text(
        text=get_localization(user_language_code).catalog_prompts_choose_prompt(prompts),
        reply_markup=build_prompts_catalog_keyboard(user_language_code, prompts),
    )


@catalog_router.callback_query(lambda c: c.data.startswith('catalog_prompt:'))
async def handle_catalog_prompt_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    prompt_id = callback_query.data.split(':')[1]
    if prompt_id == 'back':
        await handle_catalog_prompts_category(
            callback_query.message,
            user_id,
            state,
        )
    else:
        await state.update_data(prompt_id=prompt_id)
        await handle_catalog_prompt(
            callback_query.message,
            user_id,
            state,
        )


async def handle_catalog_prompt(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(user_id, state.storage)
    user_data = await state.get_data()

    prompt = await get_prompt(user_data.get('prompt_id'))
    products = []
    for product_id in prompt.product_ids:
        product = await get_product(product_id)
        if product:
            products.append(product)

    await message.edit_text(
        text=get_localization(user_language_code).catalog_prompts_info_prompt(prompt, products),
        reply_markup=build_prompts_catalog_chosen_keyboard(user_language_code, prompt),
    )


@catalog_router.callback_query(lambda c: c.data.startswith('catalog_prompt_chosen:'))
async def handle_catalog_prompt_chosen_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    action = callback_query.data.split(':')[1]
    if action == 'back':
        await handle_catalog_prompts_subcategory(
            callback_query.message,
            user_id,
            state,
        )
    else:
        user_language_code = await get_user_language(user_id, state.storage)

        prompt_id = callback_query.data.split(':')[2]
        prompt = await get_prompt(prompt_id)

        if action == 'short':
            await state.update_data(prompt_text=prompt.short_prompts.get(user_language_code))
        elif action == 'long':
            await state.update_data(prompt_text=prompt.long_prompts.get(user_language_code))
        elif action == 'examples':
            products = []
            media = []
            blobs = await firebase.bucket.list_blobs(prefix=f'prompts/{prompt.id}')

            for blob in blobs:
                blob_name = blob.split('/')[-1]
                blob_id = blob_name.split('.')[0]
                if blob_id and blob_id in prompt.product_ids:
                    product = await get_product(blob_id)
                    products.append(product)

            for blob in blobs:
                blob_name = blob.split('/')[-1]
                blob_id = blob_name.split('.')[0]
                if blob_id and blob_id in prompt.product_ids:
                    media_caption = get_localization(user_language_code).catalog_prompts_examples(products)
                    media.append(
                        InputMediaPhoto(
                            media=URLInputFile(firebase.get_public_url(blob), filename=blob_name, timeout=300),
                            caption=media_caption if len(media) == 0 else None,
                            show_caption_above_media=True,
                        )
                    )

            await callback_query.message.answer_media_group(
                media=media,
            )

            return
        else:
            return

        await handle_catalog_prompt_info(
            callback_query.message,
            user_id,
            state,
        )


async def handle_catalog_prompt_info(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(user_id, state.storage)
    user_data = await state.get_data()

    text = user_data.get('prompt_text')
    await message.edit_text(
        text=text,
        reply_markup=build_prompts_catalog_copy_keyboard(
            user_language_code,
            text,
        ),
    )


@catalog_router.callback_query(lambda c: c.data.startswith('catalog_prompt_info_chosen:'))
async def handle_catalog_prompt_info_chosen_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    action = callback_query.data.split(':')[1]
    if action == 'back':
        await handle_catalog_prompt(
            callback_query.message,
            user_id,
            state,
        )
