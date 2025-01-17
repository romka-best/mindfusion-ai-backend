from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.models.common import Model, Quota
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.user import UserSettings
from bot.database.operations.generation.getters import get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import get_started_requests_by_user_id_and_product_id
from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_error_info import send_error_info
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.locales.translate_text import translate_text
from bot.integrations.replicate_ai import create_music_gen_melody
from bot.keyboards.common.common import build_cancel_keyboard, build_error_keyboard
from bot.keyboards.ai.music_gen import build_music_gen_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode
from bot.states.ai.music_gen import MusicGen

music_gen_router = Router()

PRICE_MUSIC_GEN = 0.0014


@music_gen_router.message(Command('music_gen'))
async def music_gen(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.MUSIC_GEN:
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.MUSIC_GEN)
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=reply_markup,
        )
    else:
        user.current_model = Model.MUSIC_GEN
        await update_user(user_id, {
            'current_model': user.current_model,
        })

        text = await get_switched_to_ai_model(
            user,
            get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
            user_language_code,
        )
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.MUSIC_GEN)
        answered_message = await message.answer(
            text=text,
            reply_markup=reply_markup,
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_chat_message(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass

    await handle_music_gen(message.bot, str(message.chat.id), state, user_id)


async def handle_music_gen(bot: Bot, chat_id: str, state: FSMContext, user_id: str, text=None):
    user_language_code = await get_user_language(str(user_id), state.storage)

    if text is None:
        await bot.send_message(
            chat_id=chat_id,
            text=get_localization(user_language_code).MUSIC_GEN_INFO,
        )
    else:
        reply_markup = build_music_gen_keyboard(user_language_code)
        await bot.send_message(
            chat_id=chat_id,
            text=get_localization(user_language_code).MUSIC_GEN_TYPE_SECONDS,
            reply_markup=reply_markup,
        )

        await state.set_state(MusicGen.waiting_for_music_gen_duration)
        await state.update_data(music_gen_prompt=text)


@music_gen_router.callback_query(lambda c: c.data.startswith('music_gen:'))
async def music_gen_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    duration = callback_query.data.split(':')[1]
    await handle_music_gen_selection(
        callback_query.message,
        str(callback_query.from_user.id),
        duration,
        state,
    )


async def handle_music_gen_selection(
    message: Message,
    user_id: str,
    duration: str,
    state: FSMContext,
):
    user = await get_user(str(user_id))
    user_language_code = await get_user_language(str(user_id), state.storage)
    user_data = await state.get_data()

    try:
        duration = (int(duration) // 10) * 10
    except (TypeError, ValueError):
        reply_markup = build_cancel_keyboard(user_language_code)
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=reply_markup,
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

    async with ChatActionSender.record_voice(bot=message.bot, chat_id=message.chat.id):
        quota = user.daily_limits[Quota.MUSIC_GEN] + user.additional_usage_quota[Quota.MUSIC_GEN]
        prompt = user_data.get('music_gen_prompt')

        if not prompt:
            await handle_music_gen(message.bot, user.telegram_chat_id, state, user_id)

            await processing_sticker.delete()
            await processing_message.delete()
            await message.delete()
            return

        if quota * 10 < duration:
            reply_markup = build_cancel_keyboard(user_language_code)
            await message.reply(
                text=get_localization(user_language_code).music_gen_forbidden_error(quota * 10),
                reply_markup=reply_markup,
                allow_sending_without_reply=True,
            )

            await processing_sticker.delete()
            await processing_message.delete()
        elif duration < 10:
            reply_markup = build_cancel_keyboard(user_language_code)
            await message.reply(
                text=get_localization(user_language_code).MUSIC_GEN_MIN_ERROR,
                reply_markup=reply_markup,
                allow_sending_without_reply=True,
            )

            await processing_sticker.delete()
            await processing_message.delete()
        elif duration > 600:
            reply_markup = build_cancel_keyboard(user_language_code)
            await message.reply(
                text=get_localization(user_language_code).MUSIC_GEN_MAX_ERROR,
                reply_markup=reply_markup,
                allow_sending_without_reply=True,
            )

            await processing_sticker.delete()
            await processing_message.delete()
        else:
            product = await get_product_by_quota(Quota.MUSIC_GEN)

            user_not_finished_requests = await get_started_requests_by_user_id_and_product_id(user.id, product.id)

            if len(user_not_finished_requests):
                await message.reply(
                    text=get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST,
                    allow_sending_without_reply=True,
                )

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
                if user_language_code != LanguageCode.EN:
                    prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)
                result_id = await create_music_gen_melody(prompt, duration)
                await write_generation(
                    id=result_id,
                    request_id=request.id,
                    product_id=product.id,
                    has_error=result_id is None,
                    details={
                        'prompt': prompt,
                        'duration': duration,
                    }
                )
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
                    hashtags=['music_gen'],
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


@music_gen_router.message(MusicGen.waiting_for_music_gen_duration, ~F.text.startswith('/'))
async def music_gen_duration_sent(message: Message, state: FSMContext):
    await handle_music_gen_selection(message, str(message.from_user.id), message.text, state)
