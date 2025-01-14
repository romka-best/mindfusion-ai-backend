import asyncio
import random

import aiohttp
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    URLInputFile,
)
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Model, Quota, SendType, Currency
from bot.database.models.face_swap_package import (
    FaceSwapPackage,
    FaceSwapPackageStatus,
    FaceSwapFileData,
    UsedFaceSwapPackage,
)
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.transaction import TransactionType
from bot.database.models.user import User, UserGender, UserSettings
from bot.database.operations.face_swap_package.getters import (
    get_face_swap_package,
    get_face_swap_packages_by_gender,
    get_face_swap_package_by_name_and_gender,
    get_used_face_swap_packages_by_user_id,
    get_used_face_swap_package_by_user_id_and_package_id,
)
from bot.database.operations.face_swap_package.writers import write_used_face_swap_package
from bot.database.operations.generation.getters import get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import get_started_requests_by_user_id_and_product_id
from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.integrations.face_swap import generate_face_swap_video, get_face_swap_video_generation
from bot.integrations.replicateAI import create_face_swap_images, create_flux_face_swap_image
from bot.keyboards.ai.face_swap import (
    build_face_swap_choose_keyboard,
    build_face_swap_package_keyboard,
)
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_cancel_keyboard, build_error_keyboard, build_suggestions_keyboard
from bot.keyboards.common.profile import build_profile_gender_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.translate_text import translate_text
from bot.locales.types import LanguageCode
from bot.states.ai.face_swap import FaceSwap
from bot.states.common.profile import Profile

face_swap_router = Router()

PRICE_FACE_SWAP = 0.0014
PRICE_FACE_SWAP_VIDEO = 0.02


def count_active_files(files_list: list[FaceSwapFileData]) -> int:
    active_count = sum(
        1 for file in files_list if file.get('status', FaceSwapPackageStatus.LEGACY) == FaceSwapPackageStatus.PUBLIC
    )

    return active_count


@face_swap_router.message(Command('face_swap'))
async def face_swap(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.FACE_SWAP:
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.FACE_SWAP)
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=reply_markup,
        )
    else:
        user.current_model = Model.FACE_SWAP
        await update_user(user_id, {
            'current_model': user.current_model,
        })

        text = await get_switched_to_ai_model(
            user,
            get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
            user_language_code,
        )
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.FACE_SWAP)
        answered_message = await message.answer(
            text=text,
            reply_markup=reply_markup,
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
        await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)

    await handle_face_swap(message.bot, user.telegram_chat_id, state, user_id)


async def handle_face_swap(bot: Bot, chat_id: str, state: FSMContext, user_id: str):
    user = await get_user(str(user_id))
    user_language_code = await get_user_language(str(user_id), state.storage)

    if user.settings[Model.FACE_SWAP][UserSettings.GENDER] == UserGender.UNSPECIFIED:
        reply_markup = build_profile_gender_keyboard(user_language_code)
        await bot.send_message(
            chat_id=chat_id,
            text=get_localization(user_language_code).PROFILE_TELL_ME_YOUR_GENDER,
            reply_markup=reply_markup,
        )
    else:
        try:
            blobs = await firebase.bucket.list_blobs(prefix=f'users/avatars/{user_id}.')
            if len(blobs) > 0:
                user_photo = blobs[-1]
            else:
                user_photo = f'users/avatars/{user_id}.jpeg'
            await firebase.bucket.get_blob(user_photo)

            used_face_swap_packages = await get_used_face_swap_packages_by_user_id(user_id)
            face_swap_packages = await get_face_swap_packages_by_gender(
                gender=user.settings[Model.FACE_SWAP][UserSettings.GENDER],
                status=FaceSwapPackageStatus.PUBLIC,
            )
            has_more = False
            for used_face_swap_package in used_face_swap_packages:
                face_swap_package_files = await get_face_swap_package(used_face_swap_package.package_id)
                face_swap_package_quantity = count_active_files(face_swap_package_files.files)
                face_swap_package_used_images = len(used_face_swap_package.used_images)
                remain_images = face_swap_package_quantity - face_swap_package_used_images
                if remain_images > 0:
                    has_more = True
                    break
            if has_more or not used_face_swap_packages or len(face_swap_packages) > len(used_face_swap_packages):
                face_swap_packages = await get_face_swap_packages_by_gender(
                    gender=user.settings[Model.FACE_SWAP][UserSettings.GENDER],
                    status=FaceSwapPackageStatus.PUBLIC,
                )

                photo_path = f'face_swap/main.png'
                photo = await firebase.bucket.get_blob(photo_path)
                photo_link = firebase.get_public_url(photo.name)

                await bot.send_photo(
                    chat_id=chat_id,
                    photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
                    caption=get_localization(user_language_code).FACE_SWAP_INFO,
                    reply_markup=build_face_swap_choose_keyboard(user_language_code, face_swap_packages),
                )
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=get_localization(user_language_code).FACE_SWAP_GENERATIONS_IN_PACKAGES_ENDED,
                    reply_markup=build_suggestions_keyboard(user_language_code),
                )
        except aiohttp.ClientResponseError:
            photo_path = 'users/avatars/example.png'
            photo = await firebase.bucket.get_blob(photo_path)
            photo_link = firebase.get_public_url(photo.name)

            reply_markup = build_cancel_keyboard(user_language_code)
            await bot.send_photo(
                chat_id=chat_id,
                photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
                caption=get_localization(user_language_code).PROFILE_SEND_ME_YOUR_PICTURE,
                reply_markup=reply_markup
            )
            await state.set_state(Profile.waiting_for_photo)


async def handle_face_swap_prompt(
    message: Message,
    state: FSMContext,
    user: User,
):
    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    prompt = user_data.get('recognized_text', None)
    if prompt is None:
        if message.caption:
            prompt = message.caption
        elif message.text:
            prompt = message.text
        else:
            prompt = ''

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_face_swap_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        product = await get_product_by_quota(Quota.FACE_SWAP)

        user_not_finished_requests = await get_started_requests_by_user_id_and_product_id(user.id, product.id)

        if len(user_not_finished_requests):
            await message.reply(
                text=get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST,
                allow_sending_without_reply=True,
            )

            await processing_sticker.delete()
            await processing_message.delete()
            return

        try:
            user_photo_blobs = await firebase.bucket.list_blobs(prefix=f'users/avatars/{user.id}.')
            if len(user_photo_blobs) > 0:
                user_photo = user_photo_blobs[-1]
            else:
                user_photo = f'users/avatars/{user.id}.jpeg'
            user_photo = await firebase.bucket.get_blob(user_photo)
            user_photo_link = firebase.get_public_url(user_photo.name)

            if prompt and user_language_code != LanguageCode.EN:
                prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)
            user_gender = 'male' if user.settings[Model.FACE_SWAP][UserSettings.GENDER] == UserGender.MALE else 'female'
            prompt += f'. A photo of a {user_gender} person img'
            result_id = await create_flux_face_swap_image(
                prompt,
                user_photo_link,
            )

            request = await write_request(
                user_id=user.id,
                processing_message_ids=[processing_sticker.message_id, processing_message.message_id],
                product_id=product.id,
                requested=1,
            )

            await write_generation(
                id=result_id,
                request_id=request.id,
                product_id=product.id,
                has_error=result_id is None,
                details={
                    'prompt': prompt,
                }
            )
        except aiohttp.ClientResponseError:
            photo_path = 'users/avatars/example.png'
            photo = await firebase.bucket.get_blob(photo_path)
            photo_link = firebase.get_public_url(photo.name)

            reply_markup = build_cancel_keyboard(user_language_code)
            await message.answer_photo(
                photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
                caption=get_localization(user_language_code).PROFILE_SEND_ME_YOUR_PICTURE,
                reply_markup=reply_markup
            )
            await state.set_state(Profile.waiting_for_photo)

            await processing_sticker.delete()
            await processing_message.delete()
        except Exception as e:
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
            )

            reply_markup = build_error_keyboard(user_language_code)
            await message.answer(
                text=get_localization(user_language_code).ERROR,
                reply_markup=reply_markup,
            )
            await send_error_info(
                bot=message.bot,
                user_id=user.id,
                info=str(e),
                hashtags=['face_swap'],
            )

            request.status = RequestStatus.FINISHED
            await update_request(request.id, {
                'status': request.status
            })

            generations = await get_generations_by_request_id(request.id)
            for generation in generations:
                generation.status = GenerationStatus.FINISHED,
                generation.has_error = True
                await update_generation(
                    generation.id,
                    {
                        'status': generation.status,
                        'has_error': generation.has_error,
                    },
                )

            await processing_sticker.delete()
            await processing_message.delete()


async def handle_face_swap_video(
    message: Message,
    state: FSMContext,
    user: User,
    video_link: str,
    video_duration: int,
):
    user_language_code = await get_user_language(user.id, state.storage)

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.VIDEO_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_face_swap_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_video(bot=message.bot, chat_id=message.chat.id):
        product = await get_product_by_quota(Quota.FACE_SWAP)

        user_not_finished_requests = await get_started_requests_by_user_id_and_product_id(user.id, product.id)

        if len(user_not_finished_requests):
            await message.reply(
                text=get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST,
                allow_sending_without_reply=True,
            )

            await processing_sticker.delete()
            await processing_message.delete()
            return

        try:
            user_photo_blobs = await firebase.bucket.list_blobs(prefix=f'users/avatars/{user.id}.')
            if len(user_photo_blobs) > 0:
                user_photo = user_photo_blobs[-1]
            else:
                user_photo = f'users/avatars/{user.id}.jpeg'
            user_photo = await firebase.bucket.get_blob(user_photo)
            user_photo_link = firebase.get_public_url(user_photo.name)
        except aiohttp.ClientResponseError:
            photo_path = 'users/avatars/example.png'
            photo = await firebase.bucket.get_blob(photo_path)
            photo_link = firebase.get_public_url(photo.name)

            reply_markup = build_cancel_keyboard(user_language_code)
            await message.answer_photo(
                photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
                caption=get_localization(user_language_code).PROFILE_SEND_ME_YOUR_PICTURE,
                reply_markup=reply_markup
            )
            await state.set_state(Profile.waiting_for_photo)

            await processing_sticker.delete()
            await processing_message.delete()
            return

        request = await write_request(
            user_id=user.id,
            processing_message_ids=[processing_sticker.message_id, processing_message.message_id],
            product_id=product.id,
            requested=1,
        )

        try:
            print(video_link)
            result_id = await generate_face_swap_video(
                user_photo_link,
                video_link,
            )

            generation = await write_generation(
                id=result_id,
                request_id=request.id,
                product_id=product.id,
                has_error=result_id is None,
                details={
                    'video_link': video_link,
                }
            )

            for i in range(10):
                await asyncio.sleep(30)

                video_generation = await get_face_swap_video_generation(result_id)
                print(video_generation)
                if video_generation.get('progress') == 100:
                    video_result_url = video_generation.get('output')[0]
                    footer_text = f'\n\n📹 {user.daily_limits[Quota.FACE_SWAP] + user.additional_usage_quota[Quota.FACE_SWAP]}' \
                        if user.settings[Model.FACE_SWAP][UserSettings.SHOW_USAGE_QUOTA] and \
                           user.daily_limits[Quota.FACE_SWAP] != float('inf') else ''
                    if user.settings[Model.FACE_SWAP][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
                        await message.reply_document(
                            caption=f'{get_localization(user_language_code).GENERATION_VIDEO_SUCCESS}{footer_text}',
                            document=video_result_url,
                            allow_sending_without_reply=True,
                        )
                    else:
                        await message.reply_video(
                            caption=f'{get_localization(user_language_code).GENERATION_VIDEO_SUCCESS}{footer_text}',
                            video=video_result_url,
                            allow_sending_without_reply=True,
                        )

                    total_price = PRICE_FACE_SWAP_VIDEO * video_generation.get('need_credits')
                    update_tasks = [
                        update_generation(generation.id, {
                            'status': GenerationStatus.FINISHED,
                            'result': video_result_url,
                        }),
                        update_request(request.id, {
                            'status': RequestStatus.FINISHED,
                        }),
                        write_transaction(
                            user_id=user.id,
                            type=TransactionType.EXPENSE,
                            product_id=generation.product_id,
                            amount=total_price,
                            clear_amount=total_price,
                            currency=Currency.USD,
                            quantity=1,
                            details={
                                'result': video_result_url,
                                'video_link': video_link,
                                'has_error': False,
                            },
                        ),
                        update_user_usage_quota(
                            user,
                            Quota.FACE_SWAP,
                            video_duration,
                        ),
                    ]

                    await asyncio.gather(*update_tasks)
                    break
            else:
                raise TimeoutError('Timeout Error')
        except Exception as e:
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
            )

            reply_markup = build_error_keyboard(user_language_code)
            await message.answer(
                text=get_localization(user_language_code).ERROR,
                reply_markup=reply_markup,
            )
            await send_error_info(
                bot=message.bot,
                user_id=user.id,
                info=str(e),
                hashtags=['face_swap'],
            )

            await update_request(request.id, {
                'status': RequestStatus.FINISHED
            })

            generations = await get_generations_by_request_id(request.id)
            for generation in generations:
                generation.status = GenerationStatus.FINISHED,
                generation.has_error = True
                await update_generation(
                    generation.id,
                    {
                        'status': generation.status,
                        'has_error': generation.has_error,
                    },
                )

            await processing_sticker.delete()
            await processing_message.delete()


@face_swap_router.callback_query(lambda c: c.data.startswith('face_swap_choose:'))
async def face_swap_choose_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user = await get_user(str(callback_query.from_user.id))
    user_language_code = await get_user_language(user.id, state.storage)
    user_available_images = user.daily_limits[Quota.FACE_SWAP] + user.additional_usage_quota[Quota.FACE_SWAP]

    package_name = callback_query.data.split(':')[1]

    face_swap_package = await get_face_swap_package_by_name_and_gender(
        package_name,
        user.settings[Model.FACE_SWAP][UserSettings.GENDER],
    )
    used_face_swap_package = await get_used_face_swap_package_by_user_id_and_package_id(user.id, face_swap_package.id)
    if used_face_swap_package is None:
        used_face_swap_package = await write_used_face_swap_package(user.id, face_swap_package.id, [])
    face_swap_package_quantity = count_active_files(face_swap_package.files)
    face_swap_package_used_images = len(used_face_swap_package.used_images)

    suggested_quantities = set()
    maximum_quantity = face_swap_package_quantity - face_swap_package_used_images
    if maximum_quantity > 0:
        suggested_quantities.add(1)
        if maximum_quantity // 4 > 0:
            suggested_quantities.add(maximum_quantity // 4)
        if maximum_quantity // 2 > maximum_quantity // 4:
            suggested_quantities.add(maximum_quantity // 2)
        if maximum_quantity > maximum_quantity // 2:
            suggested_quantities.add(maximum_quantity)

    await callback_query.message.edit_caption(
        caption=get_localization(user_language_code).face_swap_choose_package(
            name=face_swap_package.translated_names.get(user_language_code, face_swap_package.name),
            available_images=user_available_images,
            total_images=face_swap_package_quantity,
            used_images=face_swap_package_used_images
        ),
        reply_markup=build_face_swap_package_keyboard(user_language_code, sorted(list(suggested_quantities))),
    )

    await state.update_data(face_swap_package_name=face_swap_package.name)
    await state.update_data(maximum_quantity=maximum_quantity)
    if maximum_quantity > 0:
        await state.set_state(FaceSwap.waiting_for_face_swap_quantity)


@face_swap_router.callback_query(lambda c: c.data.startswith('face_swap_package:'))
async def handle_face_swap_package_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    action = callback_query.data.split(':')[1]

    if action == 'back':
        user = await get_user(user_id)
        user_language_code = await get_user_language(user_id, state.storage)

        face_swap_packages = await get_face_swap_packages_by_gender(
            gender=user.settings[Model.FACE_SWAP][UserSettings.GENDER],
            status=FaceSwapPackageStatus.PUBLIC,
        )
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).FACE_SWAP_INFO,
            reply_markup=build_face_swap_choose_keyboard(user_language_code, face_swap_packages),
        )

        await state.clear()
    else:
        await face_swap_quantity_handler(callback_query.message, state, user_id, action)


def select_unique_images(
    face_swap_package: FaceSwapPackage,
    used_face_swap_package: UsedFaceSwapPackage,
    quantity: int,
):
    unique_images = []

    available_images = [
        file for file in face_swap_package.files if file['name'] not in used_face_swap_package.used_images
    ]

    while len(unique_images) < quantity and available_images:
        selected_image = random.choice(available_images)
        unique_images.append(selected_image['name'])
        available_images.remove(selected_image)
        used_face_swap_package.used_images.append(selected_image['name'])

    return unique_images


async def generate_face_swap_images(
    quantity: int,
    gender: str,
    face_swap_package: FaceSwapPackage,
    used_face_swap_package: UsedFaceSwapPackage,
    user_photo_link: str
):
    random_names = select_unique_images(face_swap_package, used_face_swap_package, quantity)
    random_images = [
        {
            'target_image': firebase.get_public_url(
                f'face_swap/{gender}/{face_swap_package.name.lower()}/{random_names[i]}'
            ),
            'source_image': user_photo_link,
        } for i in range(quantity)
    ]

    results = await create_face_swap_images(random_images)
    return results, random_names


async def face_swap_quantity_handler(message: Message, state: FSMContext, user_id: str, chosen_quantity: str):
    user = await get_user(str(user_id))
    user_language_code = await get_user_language(str(user_id), state.storage)
    user_data = await state.get_data()

    try:
        quantity = int(chosen_quantity)
    except (TypeError, ValueError):
        reply_markup = build_cancel_keyboard(user_language_code)
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=reply_markup,
            allow_sending_without_reply=True,
        )

        return

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_face_swap_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        quota = user.daily_limits[Quota.FACE_SWAP] + user.additional_usage_quota[Quota.FACE_SWAP]
        name = user_data.get('face_swap_package_name')
        face_swap_package_quantity = user_data.get('maximum_quantity')
        if not name or not face_swap_package_quantity:
            await handle_face_swap(message.bot, user.telegram_chat_id, state, user_id)

            await processing_sticker.delete()
            await processing_message.delete()
            await message.delete()
            return

        face_swap_package = await get_face_swap_package_by_name_and_gender(
            name,
            user.settings[Model.FACE_SWAP][UserSettings.GENDER]
        )

        if quota < quantity:
            reply_markup = build_cancel_keyboard(user_language_code)
            await message.answer(
                text=get_localization(user_language_code).face_swap_package_forbidden_error(quota),
                reply_markup=reply_markup,
            )
        elif quantity < 1:
            reply_markup = build_cancel_keyboard(user_language_code)
            await message.answer(
                text=get_localization(user_language_code).FACE_SWAP_MIN_ERROR,
                reply_markup=reply_markup,
            )
        elif face_swap_package_quantity < quantity:
            reply_markup = build_cancel_keyboard(user_language_code)
            await message.answer(
                text=get_localization(user_language_code).FACE_SWAP_MAX_ERROR,
                reply_markup=reply_markup,
            )
        else:
            product = await get_product_by_quota(Quota.FACE_SWAP)

            user_not_finished_requests = await get_started_requests_by_user_id_and_product_id(user.id, product.id)

            if len(user_not_finished_requests):
                await message.reply(
                    text=get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST,
                    allow_sending_without_reply=True,
                )

                await processing_sticker.delete()
                await processing_message.delete()
                return

            user_photo_blobs = await firebase.bucket.list_blobs(prefix=f'users/avatars/{user_id}.')
            user_photo = await firebase.bucket.get_blob(user_photo_blobs[-1])
            user_photo_link = firebase.get_public_url(user_photo.name)
            used_face_swap_package = await get_used_face_swap_package_by_user_id_and_package_id(
                user.id,
                face_swap_package.id,
            )

            request = await write_request(
                user_id=user.id,
                processing_message_ids=[processing_sticker.message_id, processing_message.message_id],
                product_id=product.id,
                requested=quantity,
                details={
                    'is_test': False,
                    'face_swap_package_id': face_swap_package.id,
                    'face_swap_package_name': face_swap_package.name,
                },
            )

            try:
                results, random_names = await generate_face_swap_images(
                    quantity,
                    user.settings[Model.FACE_SWAP][UserSettings.GENDER].lower(),
                    face_swap_package,
                    used_face_swap_package,
                    user_photo_link,
                )
                tasks = []
                for (i, result) in enumerate(results):
                    if result is not None:
                        tasks.append(
                            write_generation(
                                id=result,
                                request_id=request.id,
                                product_id=product.id,
                                has_error=result is None,
                                details={
                                    'used_face_swap_package_id': used_face_swap_package.id,
                                    'used_face_swap_package_used_image': random_names[i],
                                }
                            )
                        )
                await asyncio.gather(*tasks)

                await state.update_data(maximum_quantity=face_swap_package_quantity - quantity)
            except Exception as e:
                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
                )

                reply_markup = build_error_keyboard(user_language_code)
                await message.answer(
                    text=get_localization(user_language_code).ERROR,
                    reply_markup=reply_markup,
                )

                await send_error_info(
                    bot=message.bot,
                    user_id=user.id,
                    info=str(e),
                    hashtags=['face_swap'],
                )

                request.status = RequestStatus.FINISHED
                await update_request(request.id, {
                    'status': request.status
                })

                generations = await get_generations_by_request_id(request.id)
                for generation in generations:
                    generation.status = GenerationStatus.FINISHED,
                    generation.has_error = True
                    await update_generation(
                        generation.id,
                        {
                            'status': generation.status,
                            'has_error': generation.has_error,
                        },
                    )

                await processing_sticker.delete()
                await processing_message.delete()


@face_swap_router.message(FaceSwap.waiting_for_face_swap_quantity, ~F.text.startswith('/'))
async def face_swap_quantity_sent(message: Message, state: FSMContext):
    await face_swap_quantity_handler(message, state, str(message.from_user.id), message.text)
