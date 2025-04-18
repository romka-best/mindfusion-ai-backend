import asyncio

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import MessageEffect, MessageSticker, config
from bot.database.models.common import Model, Quota, SunoMode
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.user import UserSettings
from bot.database.operations.generation.getters import get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import (
    get_started_requests_by_user_id_and_product_id,
)
from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_error_info import send_error_info
from bot.integrations.suno import generate_song
from bot.keyboards.ai.model import (
    build_model_limit_exceeded_keyboard,
    build_switched_to_ai_keyboard,
)
from bot.keyboards.ai.suno import (
    build_suno_custom_mode_genres_keyboard,
    build_suno_custom_mode_lyrics_keyboard,
    build_suno_keyboard,
    build_suno_simple_mode_keyboard,
)
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.translate_text import translate_text
from bot.locales.types import LanguageCode
from bot.states.ai.suno import Suno

suno_router = Router()

PRICE_SUNO = 0.0348


@suno_router.message(Command("suno"))
async def suno(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.SUNO:
        await message.answer(
            text=get_localization(
                user_language_code
            ).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.SUNO),
        )
    else:
        user.current_model = Model.SUNO
        await update_user(
            user_id,
            {
                "current_model": user.current_model,
            },
        )

        text = await get_switched_to_ai_model(
            user,
            get_quota_by_model(
                user.current_model,
                user.settings[user.current_model][UserSettings.VERSION],
            ),
            user_language_code,
        )
        answered_message = await message.answer(
            text=text,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.SUNO),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(
                user.telegram_chat_id, answered_message.message_id
            )
        except (TelegramBadRequest, TelegramRetryAfter):
            pass

    await handle_suno(message.bot, str(message.chat.id), state, user_id)


async def handle_suno(bot: Bot, chat_id: str, state: FSMContext, user_id: str):
    user_language_code = await get_user_language(str(user_id), state.storage)

    await bot.send_message(
        chat_id=chat_id,
        text=get_localization(user_language_code).SUNO_INFO,
        reply_markup=build_suno_keyboard(user_language_code),
    )


@suno_router.callback_query(lambda c: c.data.startswith("suno:"))
async def handle_suno_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    mode = callback_query.data.split(":")[1]

    if mode == SunoMode.SIMPLE:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).SUNO_SIMPLE_MODE_PROMPT,
            reply_markup=build_suno_simple_mode_keyboard(user_language_code),
        )

        await state.set_state(Suno.waiting_for_prompt)
    elif mode == SunoMode.CUSTOM:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).SUNO_CUSTOM_MODE_LYRICS,
            reply_markup=build_suno_custom_mode_lyrics_keyboard(user_language_code),
        )

        await state.set_state(Suno.waiting_for_lyrics)

    await state.update_data(suno_mode=mode)


@suno_router.callback_query(lambda c: c.data.startswith("suno_simple_mode:"))
async def handle_suno_simple_mode_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    action = callback_query.data.split(":")[1]

    if action == "back":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).SUNO_INFO,
            reply_markup=build_suno_keyboard(user_language_code),
        )

        await state.clear()


@suno_router.message(Suno.waiting_for_prompt, ~F.text.startswith("/"))
async def suno_prompt_sent(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user(str(user_id))
    user_language_code = await get_user_language(str(user_id), state.storage)

    prompt = message.text
    if prompt is None:
        await message.reply(
            text=get_localization(user_language_code).SUNO_VALUE_ERROR,
            allow_sending_without_reply=True,
        )
        return

    if len(prompt) > 200:
        await message.reply(
            text=get_localization(user_language_code).SUNO_TOO_MANY_WORDS_ERROR,
            allow_sending_without_reply=True,
        )
        return

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.MUSIC_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_music_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_voice(bot=message.bot, chat_id=message.chat.id):
        quota = user.daily_limits[Quota.SUNO] + user.additional_usage_quota[Quota.SUNO]
        if quota < 2:
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
            )

            await message.answer(
                text=get_localization(user_language_code).model_reached_usage_limit(),
                reply_markup=build_model_limit_exceeded_keyboard(
                    user_language_code, user.had_subscription
                ),
            )

            await processing_sticker.delete()
            await processing_message.delete()
        else:
            product = await get_product_by_quota(Quota.SUNO)

            user_not_finished_requests = (
                await get_started_requests_by_user_id_and_product_id(
                    user.id, product.id
                )
            )

            if len(user_not_finished_requests):
                await message.reply(
                    text=get_localization(
                        user_language_code
                    ).MODEL_ALREADY_MAKE_REQUEST,
                    allow_sending_without_reply=True,
                )

                await processing_sticker.delete()
                await processing_message.delete()
                return

            request = await write_request(
                user_id=user.id,
                processing_message_ids=[
                    processing_sticker.message_id,
                    processing_message.message_id,
                ],
                product_id=product.id,
                requested=2,
                details={
                    "mode": SunoMode.SIMPLE,
                    "prompt": prompt,
                    "is_suggestion": False,
                },
            )

            try:
                task_id = await generate_song(
                    user.settings[Model.SUNO][UserSettings.VERSION], prompt
                )
                if task_id:
                    tasks = [
                        write_generation(
                            id=f"{task_id}-1",
                            request_id=request.id,
                            product_id=product.id,
                            has_error=False,
                            details={
                                "mode": SunoMode.SIMPLE,
                                "prompt": prompt,
                                "is_suggestion": False,
                            },
                        ),
                        write_generation(
                            id=f"{task_id}-2",
                            request_id=request.id,
                            product_id=product.id,
                            has_error=False,
                            details={
                                "mode": SunoMode.SIMPLE,
                                "prompt": prompt,
                                "is_suggestion": False,
                            },
                        ),
                    ]

                    await asyncio.gather(*tasks)
                else:
                    raise NotImplementedError("No Task Id Found in Suno Generation")
            except Exception as e:
                if (
                    "too many requests" in str(e).lower()
                    or "you have exceeded the rate limit" in str(e).lower()
                ):
                    await message.answer(
                        text=get_localization(
                            user_language_code
                        ).ERROR_SERVER_OVERLOADED,
                    )
                elif "prompt too long" in str(e).lower():
                    await message.answer(
                        text=get_localization(user_language_code).ERROR_PROMPT_TOO_LONG,
                    )

                    await handle_suno(message.bot, str(message.chat.id), state, user_id)
                elif "forbidden keywords" in str(e).lower():
                    await message.answer(
                        text=get_localization(
                            user_language_code
                        ).ERROR_REQUEST_FORBIDDEN,
                    )

                    await handle_suno(message.bot, str(message.chat.id), state, user_id)
                else:
                    await message.answer_sticker(
                        sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
                    )

                    await message.answer(
                        text=get_localization(user_language_code).ERROR,
                        reply_markup=build_error_keyboard(user_language_code),
                    )

                    await send_error_info(
                        bot=message.bot,
                        user_id=user.id,
                        info=str(e),
                        hashtags=["suno"],
                    )

                request.status = RequestStatus.FINISHED
                await update_request(request.id, {"status": request.status})

                generations = await get_generations_by_request_id(request.id)
                for generation in generations:
                    generation.status = GenerationStatus.FINISHED
                    generation.has_error = True
                    await update_generation(
                        generation.id,
                        {
                            "status": generation.status,
                            "has_error": generation.has_error,
                        },
                    )

                await processing_sticker.delete()
                await processing_message.delete()


@suno_router.callback_query(lambda c: c.data.startswith("suno_custom_mode_lyrics:"))
async def handle_suno_custom_mode_lyrics_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    action = callback_query.data.split(":")[1]

    if action == "skip":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).SUNO_CUSTOM_MODE_GENRES,
            reply_markup=build_suno_custom_mode_genres_keyboard(user_language_code),
        )

        await state.update_data(suno_lyrics="")
        await state.set_state(Suno.waiting_for_genres)
    elif action == "back":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).SUNO_INFO,
            reply_markup=build_suno_keyboard(user_language_code),
        )

        await state.clear()


@suno_router.message(Suno.waiting_for_lyrics, ~F.text.startswith("/"))
async def suno_lyrics_sent(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_language_code = await get_user_language(str(user_id), state.storage)

    lyrics = message.text
    if lyrics is None:
        await message.reply(
            text=get_localization(user_language_code).SUNO_VALUE_ERROR,
            allow_sending_without_reply=True,
        )
        return

    await message.reply(
        text=get_localization(user_language_code).SUNO_CUSTOM_MODE_GENRES,
        reply_markup=build_suno_custom_mode_genres_keyboard(user_language_code),
        allow_sending_without_reply=True,
    )

    await state.update_data(suno_lyrics=lyrics)
    await state.set_state(Suno.waiting_for_genres)


@suno_router.callback_query(lambda c: c.data.startswith("suno_custom_mode_genres:"))
async def handle_suno_custom_mode_genres_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    action = callback_query.data.split(":")[1]

    if action == "start_again":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).SUNO_INFO,
            reply_markup=build_suno_keyboard(user_language_code),
        )

        await state.clear()


@suno_router.message(Suno.waiting_for_genres, ~F.text.startswith("/"))
async def suno_genres_sent(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user(str(user_id))
    user_data = await state.get_data()
    user_language_code = await get_user_language(str(user_id), state.storage)

    lyrics = user_data.get("suno_lyrics", "")
    genres = message.text
    if genres is None:
        await message.reply(
            text=get_localization(user_language_code).SUNO_VALUE_ERROR,
            allow_sending_without_reply=True,
        )
        return

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.MUSIC_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_music_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_voice(bot=message.bot, chat_id=message.chat.id):
        quota = user.daily_limits[Quota.SUNO] + user.additional_usage_quota[Quota.SUNO]

        if quota < 2:
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
            )

            await message.answer(
                text=get_localization(user_language_code).model_reached_usage_limit(),
                reply_markup=build_model_limit_exceeded_keyboard(
                    user_language_code, user.had_subscription
                ),
            )

            await processing_sticker.delete()
            await processing_message.delete()
        else:
            product = await get_product_by_quota(Quota.SUNO)

            user_not_finished_requests = (
                await get_started_requests_by_user_id_and_product_id(
                    user.id, product.id
                )
            )

            if len(user_not_finished_requests):
                await message.reply(
                    text=get_localization(
                        user_language_code
                    ).MODEL_ALREADY_MAKE_REQUEST,
                    allow_sending_without_reply=True,
                )

                await processing_sticker.delete()
                await processing_message.delete()
                return

            try:
                if user_language_code != LanguageCode.EN:
                    genres = await translate_text(
                        genres, user_language_code, LanguageCode.EN
                    )

                if len(genres) > 120:
                    await message.reply(
                        text=get_localization(
                            user_language_code
                        ).SUNO_TOO_MANY_WORDS_ERROR,
                        allow_sending_without_reply=True,
                    )

                    await processing_sticker.delete()
                    await processing_message.delete()
                    return

                request = await write_request(
                    user_id=user.id,
                    processing_message_ids=[
                        processing_sticker.message_id,
                        processing_message.message_id,
                    ],
                    product_id=product.id,
                    requested=2,
                    details={
                        "mode": SunoMode.CUSTOM,
                        "lyrics": lyrics,
                        "genres": genres,
                        "is_suggestion": False,
                    },
                )

                task_id = await generate_song(
                    user.settings[Model.SUNO][UserSettings.VERSION],
                    lyrics,
                    False,
                    True,
                    genres,
                )
                if task_id:
                    tasks = [
                        write_generation(
                            id=f"{task_id}-1",
                            request_id=request.id,
                            product_id=product.id,
                            has_error=False,
                            details={
                                "mode": SunoMode.CUSTOM,
                                "lyrics": lyrics,
                                "genres": genres,
                                "is_suggestion": False,
                            },
                        ),
                        write_generation(
                            id=f"{task_id}-2",
                            request_id=request.id,
                            product_id=product.id,
                            has_error=False,
                            details={
                                "mode": SunoMode.CUSTOM,
                                "lyrics": lyrics,
                                "genres": genres,
                                "is_suggestion": False,
                            },
                        ),
                    ]

                    await asyncio.gather(*tasks)
                else:
                    raise NotImplementedError("No Task Id Found in Suno Generation")
            except Exception as e:
                if (
                    "too many requests" in str(e).lower()
                    or "you have exceeded the rate limit" in str(e).lower()
                ):
                    await message.answer(
                        text=get_localization(
                            user_language_code
                        ).ERROR_SERVER_OVERLOADED,
                    )
                elif "tags too long" in str(e).lower():
                    await message.answer(
                        text=get_localization(
                            user_language_code
                        ).SUNO_TOO_MANY_WORDS_ERROR,
                    )
                elif "tags contained artist name" in str(e).lower():
                    await message.answer(
                        text=get_localization(
                            user_language_code
                        ).SUNO_ARTIST_NAME_ERROR,
                    )
                elif "forbidden keywords" in str(e).lower():
                    await message.answer(
                        text=get_localization(
                            user_language_code
                        ).ERROR_REQUEST_FORBIDDEN,
                    )
                else:
                    await message.answer_sticker(
                        sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
                    )

                    await message.answer(
                        text=get_localization(user_language_code).ERROR,
                        reply_markup=build_error_keyboard(user_language_code),
                    )

                    await send_error_info(
                        bot=message.bot,
                        user_id=user.id,
                        info=str(e),
                        hashtags=["suno"],
                    )

                request.status = RequestStatus.FINISHED
                await update_request(request.id, {"status": request.status})

                generations = await get_generations_by_request_id(request.id)
                for generation in generations:
                    generation.status = GenerationStatus.FINISHED
                    generation.has_error = True
                    await update_generation(
                        generation.id,
                        {
                            "status": generation.status,
                            "has_error": generation.has_error,
                        },
                    )

                await processing_sticker.delete()
                await processing_message.delete()
