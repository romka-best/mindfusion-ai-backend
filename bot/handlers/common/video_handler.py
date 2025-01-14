import asyncio
import time
import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Video

from bot.config import config, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Model, Quota
from bot.database.operations.user.getters import get_user
from bot.handlers.ai.face_swap_handler import handle_face_swap_video
from bot.handlers.ai.gemini_video_handler import handle_gemini_video
from bot.keyboards.ai.model import build_model_limit_exceeded_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.utils.is_already_processing import is_already_processing
from bot.utils.is_messages_limit_exceeded import is_messages_limit_exceeded
from bot.utils.is_time_limit_exceeded import is_time_limit_exceeded

video_router = Router()


@video_router.message(F.video)
async def video(message: Message, state: FSMContext):
    await handle_video(message, state, message.video)


async def handle_video(message: Message, state: FSMContext, video_file: Video):
    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    current_time = time.time()
    need_exit = (
        await is_already_processing(message, state, current_time) or
        await is_messages_limit_exceeded(message, state, user, Quota.GEMINI_VIDEO) or
        await is_time_limit_exceeded(message, state, user, current_time)
    )
    if need_exit:
        return
    await state.update_data(last_request_time=current_time)

    if user.current_model == Model.GEMINI_VIDEO:
        if video_file.duration > 3600:
            await message.reply(
                text=get_localization(user_language_code).GEMINI_VIDEO_TOO_LONG_ERROR,
                allow_sending_without_reply=True,
            )
            return

        video_data_io = await message.bot.download(video_file, timeout=300)
        video_data = await asyncio.to_thread(video_data_io.read)

        video_vision_filename = f'{uuid.uuid4()}.mp4'
        video_vision_path = f'users/videos/{Quota.GEMINI_VIDEO}/{user_id}/{video_vision_filename}'
        video_vision = firebase.bucket.new_blob(video_vision_path)
        await video_vision.upload(video_data)
        video_link = firebase.get_public_url(video_vision_path)

        await handle_gemini_video(message, state, user, video_link)
    elif user.current_model == Model.FACE_SWAP:
        if sum([user.daily_limits[Quota.FACE_SWAP], user.additional_usage_quota[Quota.FACE_SWAP]]) < video_file.duration:
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
            )

            text = get_localization(user_language_code).model_reached_usage_limit()
            reply_markup = build_model_limit_exceeded_keyboard(user_language_code)
            await message.reply(
                text=text,
                reply_markup=reply_markup,
                allow_sending_without_reply=True,
            )
            return

        video_data_io = await message.bot.download(video_file, timeout=300)
        video_data = await asyncio.to_thread(video_data_io.read)

        video_vision_filename = f'{uuid.uuid4()}.mp4'
        video_vision_path = f'users/videos/{Quota.FACE_SWAP}/{user_id}/{video_vision_filename}'
        video_vision = firebase.bucket.new_blob(video_vision_path)
        await video_vision.upload(video_data)
        video_link = firebase.get_public_url(video_vision_path)

        await handle_face_swap_video(message, state, user, video_link, video_file.duration)
    else:
        await message.reply(
            text=get_localization(user_language_code).ERROR_VIDEO_FORBIDDEN,
            allow_sending_without_reply=True,
        )
