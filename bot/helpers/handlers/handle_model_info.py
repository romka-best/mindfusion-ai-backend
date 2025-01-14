from aiogram import Bot
from aiogram.fsm.context import FSMContext

from bot.database.models.common import Model
from bot.handlers.ai.face_swap_handler import handle_face_swap
from bot.handlers.ai.music_gen_handler import handle_music_gen
from bot.handlers.ai.photoshop_ai_handler import handle_photoshop_ai
from bot.handlers.ai.suno_handler import handle_suno
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


async def handle_model_info(
    bot: Bot,
    chat_id: str,
    state: FSMContext,
    model: Model,
    language_code: LanguageCode,
):
    if model == Model.EIGHTIFY:
        await bot.send_message(
            chat_id=chat_id,
            text=get_localization(language_code).EIGHTIFY_INFO,
        )
    elif model == Model.GEMINI_VIDEO:
        await bot.send_message(
            chat_id=chat_id,
            text=get_localization(language_code).GEMINI_VIDEO_INFO,
        )
    elif model == Model.FACE_SWAP:
        await handle_face_swap(
            bot=bot,
            chat_id=chat_id,
            state=state,
            user_id=chat_id,
        )
    elif model == Model.PHOTOSHOP_AI:
        await handle_photoshop_ai(
            bot=bot,
            chat_id=chat_id,
            state=state,
            user_id=chat_id,
        )
    elif model == Model.MUSIC_GEN:
        await handle_music_gen(
            bot=bot,
            chat_id=chat_id,
            state=state,
            user_id=chat_id,
        )
    elif model == Model.SUNO:
        await handle_suno(
            bot=bot,
            chat_id=chat_id,
            state=state,
            user_id=chat_id,
        )
