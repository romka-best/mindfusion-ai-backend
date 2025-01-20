from typing import cast

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.database.models.common import ModelType, Model
from bot.database.models.user import UserSettings
from bot.database.operations.user.getters import get_user
from bot.helpers.getters.get_info_by_model import get_info_by_model
from bot.keyboards.common.info import (
    build_info_keyboard,
    build_info_text_models_keyboard,
    build_info_chat_gpt_models_keyboard,
    build_info_claude_models_keyboard,
    build_info_gemini_models_keyboard,
    build_info_image_models_keyboard,
    build_info_stable_diffusion_models_keyboard,
    build_info_flux_models_keyboard,
    build_info_music_models_keyboard,
    build_info_video_models_keyboard,
    build_info_chosen_model_type_keyboard,
)
from bot.locales.main import get_user_language, get_localization

info_router = Router()


@info_router.message(Command('info'))
async def info(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    await message.answer(
        text=get_info_by_model(
            user.current_model,
            user.settings[user.current_model][UserSettings.VERSION],
            user_language_code,
        ),
        reply_markup=build_info_keyboard(
            language_code=user_language_code,
            model=user.current_model,
        ),
    )


@info_router.callback_query(lambda c: c.data.startswith('info:'))
async def info_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    await handle_info_selection(callback_query, state, callback_query.data.split(':')[1], True)


async def handle_info_selection(callback_query: CallbackQuery, state: FSMContext, model_type: str, is_edit=False):
    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    if model_type == ModelType.TEXT:
        reply_keyboard = build_info_text_models_keyboard(user_language_code)
        text = get_localization(user_language_code).INFO_TEXT_MODELS
    elif model_type == ModelType.IMAGE:
        reply_keyboard = build_info_image_models_keyboard(user_language_code)
        text = get_localization(user_language_code).INFO_IMAGE_MODELS
    elif model_type == ModelType.MUSIC:
        reply_keyboard = build_info_music_models_keyboard(user_language_code)
        text = get_localization(user_language_code).INFO_MUSIC_MODELS
    elif model_type == ModelType.VIDEO:
        reply_keyboard = build_info_video_models_keyboard(user_language_code)
        text = get_localization(user_language_code).INFO_VIDEO_MODELS
    else:
        return

    if is_edit:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_keyboard,
        )
    else:
        await callback_query.message.answer(
            text=text,
            reply_markup=reply_keyboard,
        )


@info_router.callback_query(lambda c: c.data.startswith('info_text_models:'))
async def info_text_models_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    model = cast(Model, callback_query.data.split(':')[1])
    if model == 'back':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO,
            reply_markup=build_info_keyboard(user_language_code),
        )
    elif model == Model.CHAT_GPT:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO_CHAT_GPT,
            reply_markup=build_info_chat_gpt_models_keyboard(user_language_code),
        )
    elif model == Model.CLAUDE:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO_CLAUDE,
            reply_markup=build_info_claude_models_keyboard(user_language_code),
        )
    elif model == Model.GEMINI:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO_GEMINI,
            reply_markup=build_info_gemini_models_keyboard(user_language_code),
        )
    else:
        await callback_query.message.edit_text(
            text=get_info_by_model(
                model,
                None,
                user_language_code,
            ),
            reply_markup=build_info_chosen_model_type_keyboard(user_language_code, ModelType.TEXT),
        )


@info_router.callback_query(lambda c: c.data.startswith('info_text_model:'))
async def info_text_model_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    (
        model,
        model_version,
    ) = (
        cast(Model, callback_query.data.split(':')[1]),
        callback_query.data.split(':')[2],
    )
    if model_version == 'back':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO_TEXT_MODELS,
            reply_markup=build_info_text_models_keyboard(user_language_code),
        )
    else:
        await callback_query.message.edit_text(
            text=get_info_by_model(
                model,
                model_version,
                user_language_code,
            ),
            reply_markup=build_info_chosen_model_type_keyboard(user_language_code, model),
        )


@info_router.callback_query(lambda c: c.data.startswith('info_image_models:'))
async def info_image_models_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    model = cast(Model, callback_query.data.split(':')[1])
    if model == 'back':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO,
            reply_markup=build_info_keyboard(user_language_code),
        )
    elif model == Model.STABLE_DIFFUSION:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO_STABLE_DIFFUSION,
            reply_markup=build_info_stable_diffusion_models_keyboard(user_language_code),
        )
    elif model == Model.FLUX:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO_FLUX,
            reply_markup=build_info_flux_models_keyboard(user_language_code),
        )
    else:
        await callback_query.message.edit_text(
            text=get_info_by_model(
                model,
                None,
                user_language_code,
            ),
            reply_markup=build_info_chosen_model_type_keyboard(user_language_code, ModelType.IMAGE),
        )


@info_router.callback_query(lambda c: c.data.startswith('info_image_model:'))
async def info_image_model_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    (
        model,
        model_version,
    ) = (
        cast(Model, callback_query.data.split(':')[1]),
        callback_query.data.split(':')[2],
    )
    if model_version == 'back':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO_IMAGE_MODELS,
            reply_markup=build_info_image_models_keyboard(user_language_code),
        )
    else:
        await callback_query.message.edit_text(
            text=get_info_by_model(
                model,
                model_version,
                user_language_code,
            ),
            reply_markup=build_info_chosen_model_type_keyboard(user_language_code, model),
        )


@info_router.callback_query(lambda c: c.data.startswith('info_music_models:'))
async def info_music_models_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    model = cast(Model, callback_query.data.split(':')[1])
    info_text = get_info_by_model(model, None, user_language_code)
    if info_text:
        await callback_query.message.edit_text(
            text=info_text,
            reply_markup=build_info_chosen_model_type_keyboard(user_language_code, ModelType.MUSIC),
        )
    else:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO,
            reply_markup=build_info_keyboard(user_language_code),
        )


@info_router.callback_query(lambda c: c.data.startswith('info_video_models:'))
async def info_video_models_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    model = cast(Model, callback_query.data.split(':')[1])
    info_text = get_info_by_model(model, None, user_language_code)
    if info_text:
        await callback_query.message.edit_text(
            text=info_text,
            reply_markup=build_info_chosen_model_type_keyboard(user_language_code, ModelType.VIDEO),
        )
    else:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).INFO,
            reply_markup=build_info_keyboard(user_language_code),
        )


@info_router.callback_query(lambda c: c.data.startswith('info_chosen_model_type:'))
async def info_model_type_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    action, model_type = callback_query.data.split(':')[1], callback_query.data.split(':')[2]
    if model_type == ModelType.TEXT or model_type in [Model.GROK, Model.PERPLEXITY]:
        text = get_localization(user_language_code).INFO_TEXT_MODELS
        reply_markup = build_info_text_models_keyboard(user_language_code)
    elif model_type == Model.CHAT_GPT:
        text = get_localization(user_language_code).INFO_CHAT_GPT
        reply_markup = build_info_chat_gpt_models_keyboard(user_language_code)
    elif model_type == Model.CLAUDE:
        text = get_localization(user_language_code).INFO_CLAUDE
        reply_markup = build_info_claude_models_keyboard(user_language_code)
    elif model_type == Model.GEMINI:
        text = get_localization(user_language_code).INFO_GEMINI
        reply_markup = build_info_gemini_models_keyboard(user_language_code)
    elif (
        model_type == ModelType.IMAGE or
        model_type in [
            Model.DALL_E,
            Model.MIDJOURNEY,
            Model.LUMA_PHOTON,
            Model.RECRAFT,
            Model.FACE_SWAP,
            Model.PHOTOSHOP_AI,
        ]
    ):
        text = get_localization(user_language_code).INFO_IMAGE_MODELS
        reply_markup = build_info_image_models_keyboard(user_language_code)
    elif model_type == Model.STABLE_DIFFUSION:
        text = get_localization(user_language_code).INFO_STABLE_DIFFUSION
        reply_markup = build_info_stable_diffusion_models_keyboard(user_language_code)
    elif model_type == Model.FLUX:
        text = get_localization(user_language_code).INFO_FLUX
        reply_markup = build_info_flux_models_keyboard(user_language_code)
    elif model_type == ModelType.MUSIC or model_type in [Model.MUSIC_GEN, Model.SUNO]:
        text = get_localization(user_language_code).INFO_MUSIC_MODELS
        reply_markup = build_info_music_models_keyboard(user_language_code)
    elif model_type == ModelType.VIDEO or model_type in [Model.KLING, Model.RUNWAY, Model.LUMA_RAY, Model.PIKA]:
        text = get_localization(user_language_code).INFO_VIDEO_MODELS
        reply_markup = build_info_video_models_keyboard(user_language_code)
    else:
        text = get_localization(user_language_code).INFO
        reply_markup = build_info_keyboard(user_language_code)

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_markup,
    )
