import time

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database.models.common import (
    Model,
    MidjourneyAction,
)
from bot.database.models.user import UserSettings
from bot.database.operations.user.getters import get_user
from bot.handlers.ai.chat_gpt_handler import handle_chatgpt
from bot.handlers.ai.claude_handler import handle_claude
from bot.handlers.ai.dalle_handler import handle_dall_e
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
from bot.handlers.common.common_handler import handle_help
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.utils.is_already_processing import is_already_processing
from bot.utils.is_messages_limit_exceeded import is_messages_limit_exceeded
from bot.utils.is_time_limit_exceeded import is_time_limit_exceeded

text_router = Router()


@text_router.message(F.text, ~F.text.startswith('/'))
async def handle_text(message: Message, state: FSMContext):
    user = await get_user(str(message.from_user.id))

    current_time = time.time()

    user_quota = get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION])
    if not user_quota:
        raise NotImplementedError(
            f'User model is not found: {user.current_model}'
        )

    need_exit = (
        await is_already_processing(message, state, current_time) or
        await is_messages_limit_exceeded(message, state, user, user_quota) or
        await is_time_limit_exceeded(message, state, user, current_time)
    )
    if need_exit:
        return
    await state.update_data(last_request_time=current_time)

    if user.current_model == Model.CHAT_GPT:
        await handle_chatgpt(message, state, user, user_quota)
    elif user.current_model == Model.CLAUDE:
        await handle_claude(message, state, user, user_quota)
    elif user.current_model == Model.GEMINI:
        await handle_gemini(message, state, user, user_quota)
    elif user.current_model == Model.GROK:
        await handle_grok(message, state, user)
    elif user.current_model == Model.PERPLEXITY:
        await handle_perplexity(message, state, user)
    elif user.current_model == Model.EIGHTIFY:
        await handle_eightify(message, state, user)
    elif user.current_model == Model.GEMINI_VIDEO:
        await handle_gemini_video(message, state, user, message.text)
    elif user.current_model == Model.DALL_E:
        await handle_dall_e(message, state, user)
    elif user.current_model == Model.MIDJOURNEY:
        await handle_midjourney(message, state, user, message.text, MidjourneyAction.IMAGINE)
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
        await handle_photoshop_ai(message.bot, str(message.chat.id), state, user.id)
    elif user.current_model == Model.MUSIC_GEN:
        await handle_music_gen(message.bot, str(message.chat.id), state, user.id, message.text)
    elif user.current_model == Model.SUNO:
        await handle_suno(message.bot, str(message.chat.id), state, user.id)
    elif user.current_model == Model.KLING:
        await handle_kling(message, state, user)
    elif user.current_model == Model.RUNWAY:
        await handle_runway(message, state, user)
    elif user.current_model == Model.LUMA_RAY:
        await handle_luma_ray(message, state, user)
    elif user.current_model == Model.PIKA:
        await handle_pika(message, state, user)
    else:
        raise NotImplementedError(
            f'User model is not found: {user.current_model}'
        )


@text_router.message(F.text, F.text.startswith('/'))
async def handle_unrecognized_command(message: Message, state: FSMContext):
    await handle_help(message, state)
