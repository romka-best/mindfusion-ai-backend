import asyncio
import io
import math
import os
import tempfile
import time
import uuid

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import File, Message
from filetype import filetype
from pydub import AudioSegment

from bot.database.models.common import (
    Currency,
    MidjourneyAction,
    Model,
    Quota,
)
from bot.database.models.transaction import TransactionType
from bot.database.models.user import User, UserSettings
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.handlers.ai.chat_gpt_handler import handle_chatgpt
from bot.handlers.ai.claude_handler import handle_claude
from bot.handlers.ai.dalle_handler import handle_dall_e
from bot.handlers.ai.deep_seek_handler import handle_deep_seek
from bot.handlers.ai.eightify_handler import handle_eightify
from bot.handlers.ai.face_swap_handler import handle_face_swap_prompt
from bot.handlers.ai.flux_handler import handle_flux
from bot.handlers.ai.gemini_handler import handle_gemini
from bot.handlers.ai.gemini_video_handler import handle_gemini_video
from bot.handlers.ai.grok_handler import handle_grok
from bot.handlers.ai.kling_handler import handle_kling
from bot.handlers.ai.luma_handler import handle_luma_photon, handle_luma_ray
from bot.handlers.ai.midjourney_handler import handle_midjourney
from bot.handlers.ai.music_gen_handler import handle_music_gen
from bot.handlers.ai.perplexity_handler import handle_perplexity
from bot.handlers.ai.photoshop_ai_handler import handle_photoshop_ai
from bot.handlers.ai.pika_handler import handle_pika
from bot.handlers.ai.recraft_handler import handle_recraft
from bot.handlers.ai.runway_handler import handle_runway
from bot.handlers.ai.stable_diffusion_handler import handle_stable_diffusion
from bot.handlers.ai.suno_handler import handle_suno
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.integrations.open_ai import get_response_speech_to_text
from bot.keyboards.common.common import build_buy_motivation_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode
from bot.utils.is_already_processing import is_already_processing
from bot.utils.is_messages_limit_exceeded import is_messages_limit_exceeded
from bot.utils.is_time_limit_exceeded import is_time_limit_exceeded

voice_router = Router()


async def process_voice_message(
    bot: Bot, voice: File, user: User, user_language_code: LanguageCode
):
    unique_id = uuid.uuid4()
    with tempfile.TemporaryDirectory() as tempdir:
        wav_path = os.path.join(tempdir, f"{unique_id}.wav")

        voice_ogg = io.BytesIO()
        await bot.download_file(voice.file_path, voice_ogg, timeout=300)
        extension = await asyncio.to_thread(
            lambda: filetype.guess(voice_ogg.getvalue()).extension
        )

        audio_data = {
            "file": voice_ogg,
            "format": extension,
        }
        audio = await asyncio.to_thread(AudioSegment.from_file, **audio_data)
        audio_in_seconds = audio.duration_seconds

        audio_export_data = {
            "out_f": wav_path,
            "format": "wav",
        }
        await asyncio.to_thread(audio.export, **audio_export_data)

        audio_file = await asyncio.to_thread(lambda: open(wav_path, "rb"))
        audio_file_size = await asyncio.to_thread(lambda: os.path.getsize(wav_path))
        if audio_file_size > 25 * 1024 * 1024:
            await asyncio.to_thread(audio_file.close)
            await bot.send_message(
                chat_id=user.telegram_chat_id,
                text=get_localization(user_language_code).ERROR_FILE_TOO_BIG,
            )
            return

        text = await get_response_speech_to_text(audio_file)
        await asyncio.to_thread(audio_file.close)

        product = await get_product_by_quota(Quota.VOICE_MESSAGES)

        total_price = 0.0001 * math.ceil(audio_in_seconds)
        await write_transaction(
            user_id=user.id,
            type=TransactionType.EXPENSE,
            product_id=product.id,
            amount=total_price,
            clear_amount=total_price,
            currency=Currency.USD,
            quantity=1,
            details={
                "subtype": "STT",
                "text": text,
                "has_error": False,
            },
        )

        return text


@voice_router.message(F.voice | F.audio | F.video_note)
async def handle_voice(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if not (
        user.daily_limits[Quota.VOICE_MESSAGES]
        or user.additional_usage_quota[Quota.VOICE_MESSAGES]
    ):
        await message.answer(
            text=get_localization(user_language_code).VOICE_MESSAGES_FORBIDDEN_ERROR,
            reply_markup=build_buy_motivation_keyboard(user_language_code),
        )
        return

    current_time = time.time()

    user_quota = get_quota_by_model(
        user.current_model, user.settings[user.current_model][UserSettings.VERSION]
    )
    if not user_quota:
        raise NotImplementedError(
            f"User Model Is Not Found: {user.current_model}, {user.settings[user.current_model][UserSettings.VERSION]}"
        )

    need_exit = (
        await is_already_processing(message, state, current_time)
        or await is_messages_limit_exceeded(message, state, user, user_quota)
        or await is_time_limit_exceeded(message, state, user, current_time)
    )
    if need_exit:
        return

    if message.voice:
        voice_file = await message.bot.get_file(message.voice.file_id)
    elif message.video_note:
        voice_file = await message.bot.get_file(message.video_note.file_id)
    else:
        voice_file = await message.bot.get_file(message.audio.file_id)

    text = await process_voice_message(
        message.bot, voice_file, user, user_language_code
    )
    if not text:
        return

    await state.update_data(recognized_text=text)
    if user.current_model == Model.CHAT_GPT:
        await handle_chatgpt(message, state, user, user_quota)
    elif user.current_model == Model.CLAUDE:
        await handle_claude(message, state, user, user_quota)
    elif user.current_model == Model.GEMINI:
        await handle_gemini(message, state, user, user_quota)
    elif user.current_model == Model.GROK:
        await handle_grok(message, state, user)
    elif user.current_model == Model.DEEP_SEEK:
        await handle_deep_seek(message, state, user, user_quota)
    elif user.current_model == Model.PERPLEXITY:
        await handle_perplexity(message, state, user)
    elif user.current_model == Model.EIGHTIFY:
        await handle_eightify(message, state, user)
    elif user.current_model == Model.GEMINI_VIDEO:
        await handle_gemini_video(message, state, user, text)
    elif user.current_model == Model.DALL_E:
        await handle_dall_e(message, state, user)
    elif user.current_model == Model.MIDJOURNEY:
        await handle_midjourney(message, state, user, text, MidjourneyAction.IMAGINE)
    elif user.current_model == Model.STABLE_DIFFUSION:
        await handle_stable_diffusion(message, state, user, user_quota)
    elif user.current_model == Model.FLUX:
        await handle_flux(message, state, user, user_quota)
    elif user.current_model == Model.LUMA_PHOTON:
        await handle_luma_photon(message, state, user)
    elif user.current_model == Model.RECRAFT:
        await handle_recraft(message, state, user)
    elif user.current_model == Model.FACE_SWAP:
        await handle_face_swap_prompt(message, state, user)
    elif user.current_model == Model.PHOTOSHOP_AI:
        await handle_photoshop_ai(message.bot, str(message.chat.id), state, user_id)
    elif user.current_model == Model.MUSIC_GEN:
        await handle_music_gen(message.bot, str(message.chat.id), state, user_id, text)
    elif user.current_model == Model.SUNO:
        await handle_suno(message.bot, str(message.chat.id), state, user_id)
    elif user.current_model == Model.KLING:
        await handle_kling(message, state, user)
    elif user.current_model == Model.RUNWAY:
        await handle_runway(message, state, user)
    elif user.current_model == Model.LUMA_RAY:
        await handle_luma_ray(message, state, user)
    elif user.current_model == Model.PIKA:
        await handle_pika(message, state, user)
    else:
        raise NotImplementedError(f"User model is not found: {user.current_model}")

    await state.update_data(recognized_text=None)
