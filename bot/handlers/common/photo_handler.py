import asyncio
from contextlib import AsyncExitStack
import time
import uuid
from pathlib import Path

import aiohttp
from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, URLInputFile, File, ReactionTypeEmoji
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import (
    Model,
    Quota,
    ChatGPTVersion,
    ClaudeGPTVersion,
    GeminiGPTVersion,
    GrokGPTVersion,
    MidjourneyAction,
    PhotoshopAIAction,
)
from bot.database.models.face_swap_package import FaceSwapPackageStatus
from bot.database.models.user import UserSettings
from bot.database.operations.face_swap_package.getters import (
    get_face_swap_package,
    get_used_face_swap_packages_by_user_id,
)
from bot.database.operations.face_swap_package.updaters import update_face_swap_package, update_used_face_swap_package
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import get_started_requests_by_user_id_and_product_id
from bot.database.operations.request.writers import write_request
from bot.database.operations.user.getters import get_user
from bot.handlers.admin.face_swap_handler import handle_manage_face_swap
from bot.handlers.ai.chat_gpt_handler import handle_chatgpt
from bot.handlers.ai.claude_handler import handle_claude
from bot.handlers.ai.face_swap_handler import handle_face_swap
from bot.handlers.ai.flux_handler import handle_flux
from bot.handlers.ai.gemini_handler import handle_gemini
from bot.handlers.ai.grok_handler import handle_grok
from bot.handlers.ai.kling_handler import handle_kling
from bot.handlers.ai.luma_handler import handle_luma_photon, handle_luma_ray
from bot.handlers.ai.midjourney_handler import handle_midjourney
from bot.handlers.ai.pika_handler import handle_pika
from bot.handlers.ai.runway_handler import handle_runway
from bot.handlers.ai.stable_diffusion_handler import handle_stable_diffusion
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.integrations.replicate_ai import create_face_swap_image, create_photoshop_ai_image
from bot.keyboards.admin.catalog import build_manage_catalog_create_role_confirmation_keyboard
from bot.keyboards.ai.model import build_model_limit_exceeded_keyboard
from bot.keyboards.common.common import build_cancel_keyboard, build_suggestions_keyboard, build_buy_motivation_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.middlewares.AlbumMiddleware import AlbumMiddleware
from bot.states.common.catalog import Catalog
from bot.states.ai.face_swap import FaceSwap
from bot.states.ai.photoshop_ai import PhotoshopAI
from bot.states.common.profile import Profile
from bot.utils.ctx_managers.generation_record_ctx import GenerationRecordCtx
from bot.utils.ctx_managers.processing_msgs_ctx import ProcessingMsgsCtx
from bot.utils.ctx_managers.request_record_ctx import RequestRecordCtx
from bot.utils.is_already_processing import is_already_processing
from bot.utils.is_messages_limit_exceeded import is_messages_limit_exceeded
from bot.utils.is_time_limit_exceeded import is_time_limit_exceeded
from replicate.exceptions import ReplicateError
from bot.helpers.senders.send_ai_model_internal_error import send_internal_ai_model_error
from bot.database.operations.photo_bundle.photo_bundle import PhotoBundleGateway
from bot.helpers.senders.send_photo_bundle_empty import send_photo_bundle_empty


photo_router = Router()
photo_router.message.middleware(AlbumMiddleware())


async def handle_photo(message: Message, state: FSMContext, photo_file: File):
    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    current_state = await state.get_state()
    if current_state == Profile.waiting_for_photo.state:
        processing_message = await message.reply(
            text=get_localization(user_language_code).PROFILE_UPLOADING_PHOTO,
            allow_sending_without_reply=True,
        )

        photo_data_io = await message.bot.download_file(photo_file.file_path, timeout=300)
        photo_data = await asyncio.to_thread(photo_data_io.read)
        photo_extension = photo_file.file_path.split('.')[-1]

        blob_path = f'users/avatars/{user_id}.{photo_extension}'
        existing_blobs = await firebase.bucket.list_blobs(prefix=f'users/avatars/{user_id}.')
        for existing_blob_name in existing_blobs:
            await firebase.storage.delete(
                bucket=firebase.bucket.name,
                object_name=existing_blob_name,
                timeout=300,
            )

        blob = firebase.bucket.new_blob(blob_path)
        await blob.upload(photo_data)

        await message.bot.set_message_reaction(
            message.chat.id,
            message.message_id,
            [ReactionTypeEmoji(emoji='🤩')],
            True,
        )

        used_face_swap_packages = await get_used_face_swap_packages_by_user_id(user_id)
        for used_face_swap_package in used_face_swap_packages:
            await update_used_face_swap_package(used_face_swap_package.id, {
                'used_images': [],
            })

        await processing_message.edit_text(get_localization(user_language_code).PROFILE_CHANGE_PHOTO_SUCCESS)

        await state.clear()

        if user.current_model == Model.FACE_SWAP:
            await handle_face_swap(message.bot, str(message.chat.id), state, str(message.from_user.id))
    elif current_state == Catalog.waiting_for_role_photo.state:
        user_data = await state.get_data()

        photo_data_io = await message.bot.download_file(photo_file.file_path, timeout=300)
        photo_data = await asyncio.to_thread(photo_data_io.read)

        photo_name = f'{user_data["system_role_name"]}.png'
        photo_path = f'roles/{photo_name}'
        photo_blob = firebase.bucket.new_blob(photo_path)
        await photo_blob.upload(photo_data)

        await message.answer(
            text=get_localization(user_language_code).admin_catalog_create_role_confirmation(
                role_names=user_data.get('role_names', {}),
                role_descriptions=user_data.get('role_descriptions', {}),
                role_instructions=user_data.get('role_instructions', {}),
            ),
            reply_markup=build_manage_catalog_create_role_confirmation_keyboard(user_language_code),
        )
    elif current_state == FaceSwap.waiting_for_face_swap_picture_image.state:
        user_data = await state.get_data()
        face_swap_package_id = user_data['face_swap_package_id']
        face_swap_picture_name = user_data['face_swap_picture_name']

        photo_data_io = await message.bot.download_file(photo_file.file_path, timeout=300)
        photo_data = await asyncio.to_thread(photo_data_io.read)
        photo_extension = photo_file.file_path.split('.')[-1]

        face_swap_package = await get_face_swap_package(face_swap_package_id)
        photo_name = f'{len(face_swap_package.files) + 1}_{face_swap_picture_name}.{photo_extension}'
        photo_path = f'face_swap/{user_data["gender"].lower()}/{user_data["package_name"].lower()}/{photo_name}'
        photo_blob = firebase.bucket.new_blob(photo_path)
        await photo_blob.upload(photo_data)
        face_swap_package.files.append({
            'name': photo_name,
            'status': FaceSwapPackageStatus.PRIVATE,
        })

        await update_face_swap_package(
            face_swap_package.id,
            {
                'files': face_swap_package.files
            }
        )

        await message.answer(text=get_localization(user_language_code).ADMIN_FACE_SWAP_EDIT_SUCCESS)
        await handle_manage_face_swap(message, str(message.from_user.id), state)
    elif current_state == PhotoshopAI.waiting_for_photo.state:
        # Validation
        quota = user.daily_limits[Quota.PHOTOSHOP_AI] + user.additional_usage_quota[Quota.PHOTOSHOP_AI]
        if quota < 1:
            await message.answer_sticker(sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD))

            return await message.answer(
                text=get_localization(user_language_code).model_reached_usage_limit(),
                reply_markup=build_model_limit_exceeded_keyboard(user_language_code, user.had_subscription),
            )

        product = await get_product_by_quota(Quota.PHOTOSHOP_AI)
        user_not_finished_requests = await get_started_requests_by_user_id_and_product_id(user.id, product.id)
        if len(user_not_finished_requests):
            return await message.reply(
                text=get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST,
                allow_sending_without_reply=True,
            )

        user_data = await state.get_data()
        photoshop_ai_action_name = user_data["photoshop_ai_action_name"]
        if photoshop_ai_action_name not in [
            PhotoshopAIAction.UPSCALE,
            PhotoshopAIAction.RESTORATION,
            PhotoshopAIAction.COLORIZATION,
            PhotoshopAIAction.REMOVAL_BACKGROUND,
        ]:
            return

        # Generation
        try:
            async with AsyncExitStack() as stack:
                # Prepare ctxs
                await stack.enter_async_context(ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id))
                processing_msgs_ctx = await stack.enter_async_context(
                    ProcessingMsgsCtx(
                        message,
                        config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
                        get_localization(user_language_code).model_image_processing_request(),
                    ),
                )
                request_record_ctx = await stack.enter_async_context(
                    RequestRecordCtx(
                        user_id=user_id,
                        processing_message_ids=processing_msgs_ctx.ids,
                        product_id=product.id,
                        requested=1,
                        details={
                            "type": photoshop_ai_action_name,
                        },
                    ),
                )
                gen_ctx = await stack.enter_async_context(GenerationRecordCtx())

                # Download photo
                photo_data = (await message.bot.download_file(photo_file.file_path, timeout=300)).read()
                photo_extension = photo_file.file_path.split(".")[-1]
                photo_name = f"{uuid.uuid4()}.{photo_extension}"
                photo_path = f"users/photoshop/{photoshop_ai_action_name}/{user_id}/{photo_name}"
                photo_link = firebase.get_public_url(photo_path)
                photo_photoshop = firebase.bucket.new_blob(photo_path)
                await photo_photoshop.upload(photo_data)

                # Send generation
                result = await create_photoshop_ai_image(photoshop_ai_action_name, photo_link)

                gen_ctx.add(
                    await write_generation(
                        id=result,
                        request_id=request_record_ctx.request.id,
                        product_id=product.id,
                        has_error=result is None,
                        details={
                            "type": photoshop_ai_action_name,
                        },
                    ),
                )

                await state.clear()
        except ReplicateError as e:
            if e.status == 500:
                await send_internal_ai_model_error(user_language_code, message, Model.PHOTOSHOP_AI)
            else:
                raise
    elif (
        user.current_model == Model.CHAT_GPT or
        user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Sonnet or
        user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Opus or
        user.current_model == Model.GEMINI or
        user.current_model == Model.GROK
    ):
        if not (user.daily_limits[Quota.WORK_WITH_FILES] or user.additional_usage_quota[Quota.WORK_WITH_FILES]):
            await message.answer(
                text=get_localization(user_language_code).WORK_WITH_FILES_FORBIDDEN_ERROR,
                reply_markup=build_buy_motivation_keyboard(user_language_code),
            )
            return

        if user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_Omni_Mini:
            quota = Quota.CHAT_GPT4_OMNI_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_Omni:
            quota = Quota.CHAT_GPT4_OMNI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_O_Mini:
            quota = Quota.CHAT_GPT_O_4_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V3_O:
            quota = Quota.CHAT_GPT_O_3
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_1_Mini:
            quota = Quota.CHAT_GPT_4_1_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_1:
            quota = Quota.CHAT_GPT_4_1
        elif user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Sonnet:
            quota = Quota.CLAUDE_3_SONNET
        elif user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Opus:
            quota = Quota.CLAUDE_3_OPUS
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V2_Flash:
            quota = Quota.GEMINI_2_FLASH
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V2_Pro:
            quota = Quota.GEMINI_2_PRO
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V1_Ultra:
            quota = Quota.GEMINI_1_ULTRA
        elif user.settings[user.current_model][UserSettings.VERSION] == GrokGPTVersion.V2:
            quota = Quota.GROK_2
        else:
            raise NotImplementedError(
                f'User quota is not implemented: {user.settings[user.current_model][UserSettings.VERSION]}'
            )

        current_time = time.time()
        need_exit = (
            await is_already_processing(message, state, current_time) or
            await is_messages_limit_exceeded(message, state, user, quota) or
            await is_time_limit_exceeded(message, state, user, current_time)
        )
        if need_exit:
            return

        photo_data_io = await message.bot.download_file(photo_file.file_path, timeout=300)
        photo_data = await asyncio.to_thread(photo_data_io.read)
        photo_extension = photo_file.file_path.split('.')[-1]

        photo_vision_filename = f'{uuid.uuid4()}.{photo_extension}'
        photo_vision_path = f'users/vision/{user_id}/{photo_vision_filename}'
        photo_vision = firebase.bucket.new_blob(photo_vision_path)
        await photo_vision.upload(photo_data)

        if user.current_model == Model.CHAT_GPT:
            await handle_chatgpt(message, state, user, quota, [photo_vision_filename])
        elif user.current_model == Model.CLAUDE:
            await handle_claude(message, state, user, quota, [photo_vision_filename])
        elif user.current_model == Model.GEMINI:
            await handle_gemini(message, state, user, quota, [photo_vision_filename])
        elif user.current_model == Model.GROK:
            await handle_grok(message, state, user, [photo_vision_filename])
    elif (
        user.current_model == Model.MIDJOURNEY or
        user.current_model == Model.STABLE_DIFFUSION or
        user.current_model == Model.FLUX or
        user.current_model == Model.LUMA_PHOTON
    ):
        current_time = time.time()

        user_quota = get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION])
        need_exit = (
            await is_already_processing(message, state, current_time) or
            await is_messages_limit_exceeded(message, state, user, user_quota) or
            await is_time_limit_exceeded(message, state, user, current_time)
        )
        if need_exit:
            return
        await state.update_data(last_request_time=current_time)

        photo_data_io = await message.bot.download_file(photo_file.file_path, timeout=300)
        photo_data = await asyncio.to_thread(photo_data_io.read)
        photo_extension = photo_file.file_path.split('.')[-1]

        photo_vision_filename = f'{uuid.uuid4()}.{photo_extension}'
        photo_vision_path = f'users/vision/{user_id}/{photo_vision_filename}'
        photo_vision = firebase.bucket.new_blob(photo_vision_path)
        await photo_vision.upload(photo_data)

        if user.current_model == Model.MIDJOURNEY:
            await handle_midjourney(
                message,
                state,
                user,
                message.caption,
                MidjourneyAction.IMAGINE,
                '',
                0,
                photo_vision_filename,
            )
        elif user.current_model == Model.STABLE_DIFFUSION:
            await handle_stable_diffusion(message, state, user, user_quota, photo_vision_filename)
        elif user.current_model == Model.FLUX:
            await handle_flux(message, state, user, user_quota, photo_vision_filename)
        elif user.current_model == Model.LUMA_PHOTON:
            await handle_luma_photon(message, state, user, photo_vision_filename)
    elif user.current_model == Model.FACE_SWAP:
        # Params
        quota = user.daily_limits[Quota.FACE_SWAP] + user.additional_usage_quota[Quota.FACE_SWAP]
        quantity = 1
        product = await get_product_by_quota(Quota.FACE_SWAP)

        # Validation
        if quota < quantity:
            return await message.answer(text=get_localization(user_language_code).face_swap_package_forbidden_error(quota))

        photo_bundle = await PhotoBundleGateway().get_by_user_id(user_id)
        if photo_bundle.is_empty():
            await state.clear()
            return await send_photo_bundle_empty(message, user_language_code)

        # bg_photo where face changed
        # user_photo for face to change
        bg_photo_tg_file = await message.bot.get_file(message.photo[-1].file_id)
        bg_photo_tg_file_extension = Path(bg_photo_tg_file.file_path).suffix.lstrip(".")
        bg_photo_tg_file_io = await message.bot.download_file(bg_photo_tg_file.file_path)

        bg_path = f'users/backgrounds/{user_id}/{uuid.uuid4()}.{bg_photo_tg_file_extension}'
        await firebase.storage.upload(firebase.bucket.name, bg_path, bg_photo_tg_file_io)

        bg_photo_link = firebase.get_public_url(bg_path)
        user_photo_link = firebase.get_public_url(f"users/avatars/{user_id}/{photo_bundle.photos[0].file_name}")

        # Generation
        try:
            async with AsyncExitStack() as stack:
                # Prepare ctxs
                await stack.enter_async_context(ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id))
                processing_msgs_ctx = await stack.enter_async_context(
                    ProcessingMsgsCtx(
                        message,
                        config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
                        get_localization(user_language_code).model_face_swap_processing_request(),
                    ),
                )
                request_record_ctx = await stack.enter_async_context(
                    RequestRecordCtx(
                        user_id=user_id,
                        processing_message_ids=processing_msgs_ctx.ids,
                        product_id=product.id,
                        requested=1,
                        details={
                            "is_test": False,
                        },
                    ),
                )
                gen_ctx = await stack.enter_async_context(GenerationRecordCtx())

                # Make request
                result = await create_face_swap_image(bg_photo_link, user_photo_link)

                gen_ctx.add(await write_generation(
                    id=result,
                    request_id=request_record_ctx.request.id,
                    product_id=product.id,
                    has_error=result is None,
                ))

                await state.clear()
        except ReplicateError as e:
            if e.status == 500:
                await send_internal_ai_model_error(user_language_code, message, Model.FACE_SWAP)
            else:
                raise
    elif (
        user.current_model == Model.KLING or
        user.current_model == Model.RUNWAY or
        user.current_model == Model.PIKA or
        user.current_model == Model.LUMA_RAY
    ):
        current_time = time.time()

        user_quota = get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION])
        need_exit = (
            await is_already_processing(message, state, current_time) or
            await is_messages_limit_exceeded(message, state, user, user_quota) or
            await is_time_limit_exceeded(message, state, user, current_time)
        )
        if need_exit:
            return
        await state.update_data(last_request_time=current_time)

        photo_data_io = await message.bot.download_file(photo_file.file_path, timeout=300)
        photo_data = await asyncio.to_thread(photo_data_io.read)
        photo_extension = photo_file.file_path.split('.')[-1]

        video_frame_path = f'users/video_frames/{user_quota}/{user_id}/{uuid.uuid4()}.{photo_extension}'
        video_frame_photo = firebase.bucket.new_blob(video_frame_path)
        await video_frame_photo.upload(photo_data)
        video_frame_photo_link = firebase.get_public_url(video_frame_path)

        if user.current_model == Model.KLING:
            await handle_kling(message, state, user, video_frame_photo_link)
        elif user.current_model == Model.RUNWAY:
            await handle_runway(message, state, user, video_frame_photo_link)
        elif user.current_model == Model.PIKA:
            await handle_pika(message, state, user, video_frame_photo_link)
        elif user.current_model == Model.LUMA_RAY:
            await handle_luma_ray(message, state, user, video_frame_photo_link)
    else:
        await message.reply(
            text=get_localization(user_language_code).ERROR_PHOTO_FORBIDDEN,
            reply_markup=build_suggestions_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


async def handle_album(message: Message, state: FSMContext, album: list[Message]):
    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if (
        user.current_model == Model.CHAT_GPT or
        user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Sonnet or
        user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Opus or
        user.current_model == Model.GEMINI or
        user.current_model == Model.GROK
    ):
        if not (user.daily_limits[Quota.WORK_WITH_FILES] or user.additional_usage_quota[Quota.WORK_WITH_FILES]):
            await message.answer(
                text=get_localization(user_language_code).WORK_WITH_FILES_FORBIDDEN_ERROR,
                reply_markup=build_buy_motivation_keyboard(user_language_code),
            )
            return

        if user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_Omni_Mini:
            quota = Quota.CHAT_GPT4_OMNI_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_Omni:
            quota = Quota.CHAT_GPT4_OMNI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_O_Mini:
            quota = Quota.CHAT_GPT_O_4_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V3_O:
            quota = Quota.CHAT_GPT_O_3
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_1_Mini:
            quota = Quota.CHAT_GPT_4_1_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_1:
            quota = Quota.CHAT_GPT_4_1
        elif user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Sonnet:
            quota = Quota.CLAUDE_3_SONNET
        elif user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Opus:
            quota = Quota.CLAUDE_3_OPUS
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V2_Flash:
            quota = Quota.GEMINI_2_FLASH
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V2_Pro:
            quota = Quota.GEMINI_2_PRO
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V1_Ultra:
            quota = Quota.GEMINI_1_ULTRA
        elif user.settings[user.current_model][UserSettings.VERSION] == GrokGPTVersion.V2:
            quota = Quota.GROK_2
        else:
            raise NotImplementedError(
                f'User quota is not implemented: {user.settings[user.current_model][UserSettings.VERSION]}'
            )

        current_time = time.time()
        need_exit = (
            await is_already_processing(message, state, current_time) or
            await is_messages_limit_exceeded(message, state, user, quota) or
            await is_time_limit_exceeded(message, state, user, current_time)
        )
        if need_exit:
            return

        photo_vision_filenames = []
        for file in album:
            if file.photo:
                photo_file = await message.bot.get_file(message.photo[-1].file_id)
            elif file.document.mime_type.startswith('image') and file.document.thumbnail:
                photo_file = await message.bot.get_file(file.document.file_id)
            else:
                continue

            photo_data_io = await message.bot.download_file(photo_file.file_path, timeout=300)
            photo_data = await asyncio.to_thread(photo_data_io.read)
            photo_extension = photo_file.file_path.split('.')[-1]

            photo_vision_filename = f'{uuid.uuid4()}.{photo_extension}'
            photo_vision_path = f'users/vision/{user_id}/{photo_vision_filename}'
            photo_vision = firebase.bucket.new_blob(photo_vision_path)
            await photo_vision.upload(photo_data)

            photo_vision_filenames.append(photo_vision_filename)

        if user.current_model == Model.CHAT_GPT:
            await handle_chatgpt(message, state, user, quota, photo_vision_filenames)
        elif user.current_model == Model.CLAUDE:
            await handle_claude(message, state, user, quota, photo_vision_filenames)
        elif user.current_model == Model.GEMINI:
            await handle_gemini(message, state, user, quota, photo_vision_filenames)
        elif user.current_model == Model.GROK:
            await handle_grok(message, state, user, photo_vision_filenames)
    elif (
        user.current_model == Model.MIDJOURNEY or
        user.current_model == Model.STABLE_DIFFUSION or
        user.current_model == Model.FLUX or
        user.current_model == Model.LUMA_PHOTON or
        user.current_model == Model.FACE_SWAP or
        user.current_model == Model.PHOTOSHOP_AI or
        user.current_model == Model.KLING or
        user.current_model == Model.RUNWAY or
        user.current_model == Model.PIKA
    ):
        await message.reply(
            text=get_localization(user_language_code).ERROR_ALBUM_FORBIDDEN,
            allow_sending_without_reply=True,
        )
    else:
        await message.reply(
            text=get_localization(user_language_code).ERROR_PHOTO_FORBIDDEN,
            reply_markup=build_suggestions_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


@photo_router.message(F.photo)
async def photo(message: Message, state: FSMContext, album: list[Message]):
    if len(album):
        await handle_album(message, state, album)
    else:
        photo_file = await message.bot.get_file(message.photo[-1].file_id)
        await handle_photo(message, state, photo_file)


