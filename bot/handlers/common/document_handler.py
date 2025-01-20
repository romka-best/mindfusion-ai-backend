import asyncio
import time
import uuid

from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, File

from bot.database.main import firebase
from bot.database.models.common import Model, ClaudeGPTVersion, GeminiGPTVersion, Quota
from bot.database.models.user import UserSettings
from bot.database.operations.user.getters import get_user
from bot.handlers.ai.claude_handler import handle_claude
from bot.handlers.ai.gemini_handler import handle_gemini
from bot.handlers.common.photo_handler import handle_photo, handle_album
from bot.keyboards.common.common import build_buy_motivation_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.middlewares.AlbumMiddleware import AlbumMiddleware
from bot.utils.is_already_processing import is_already_processing
from bot.utils.is_messages_limit_exceeded import is_messages_limit_exceeded
from bot.utils.is_time_limit_exceeded import is_time_limit_exceeded

document_router = Router()
document_router.message.middleware(AlbumMiddleware())


@document_router.message(F.document)
async def document(message: Message, state: FSMContext, album: list[Message]):
    if len(album):
        await handle_album(message, state, album)
    elif message.document.mime_type.startswith('image') and message.document.thumbnail:
        photo_file = await message.bot.get_file(message.document.file_id)
        await handle_photo(message, state, photo_file)
    elif (
        message.document.mime_type == 'application/pdf' or
        message.document.mime_type == 'application/x-javascript' or
        message.document.mime_type == 'text/javascript' or
        message.document.mime_type == 'text/ecmascript' or
        message.document.mime_type == 'application/x-python' or
        message.document.mime_type == 'text/x-python' or
        message.document.mime_type == 'text/x-script.phyton' or
        message.document.mime_type == 'text/plain' or
        message.document.mime_type == 'text/html' or
        message.document.mime_type == 'text/css' or
        message.document.mime_type == 'text/md' or
        message.document.mime_type == 'text/csv' or
        message.document.mime_type == 'text/xml' or
        message.document.mime_type == 'text/rtf'
    ):
        document_file = await message.bot.get_file(message.document.file_id)
        await handle_document(message, state, document_file)
    else:
        user_id = str(message.from_user.id)
        user_language_code = await get_user_language(user_id, state.storage)

        await message.reply(
            text=get_localization(user_language_code).ERROR_DOCUMENT_FORBIDDEN,
            allow_sending_without_reply=True,
        )


async def handle_document(message: Message, state: FSMContext, document_file: File):
    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if (
        user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Sonnet or
        user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V2_Flash or
        user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V1_Pro or
        user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V1_Ultra
    ):
        if not (user.daily_limits[Quota.WORK_WITH_FILES] or user.additional_usage_quota[Quota.WORK_WITH_FILES]):
            await message.answer(
                text=get_localization(user_language_code).WORK_WITH_FILES_FORBIDDEN_ERROR,
                reply_markup=build_buy_motivation_keyboard(user_language_code),
            )
            return

        if user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Sonnet:
            quota = Quota.CLAUDE_3_SONNET
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V2_Flash:
            quota = Quota.GEMINI_2_FLASH
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V1_Pro:
            quota = Quota.GEMINI_1_PRO
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V1_Ultra:
            quota = Quota.GEMINI_1_ULTRA
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
        await state.update_data(last_request_time=current_time)

        document_data_io = await message.bot.download_file(document_file.file_path, timeout=300)
        document_data = await asyncio.to_thread(document_data_io.read)
        document_extension = document_file.file_path.split('.')[-1]

        if quota in [Quota.CLAUDE_3_SONNET] and document_extension != 'pdf':
            await message.reply(
                text=get_localization(user_language_code).ERROR_DOCUMENT_FORBIDDEN,
                allow_sending_without_reply=True,
            )
            return

        document_vision_filename = f'{uuid.uuid4()}.{document_extension}'
        document_vision_path = f'users/vision/{user_id}/{document_vision_filename}'
        document_vision = firebase.bucket.new_blob(document_vision_path)
        await document_vision.upload(document_data)

        if user.current_model == Model.CLAUDE:
            await handle_claude(message, state, user, quota, [document_vision_filename], True)
        elif user.current_model == Model.GEMINI:
            await handle_gemini(message, state, user, quota, [document_vision_filename], True)
    else:
        await message.reply(
            text=get_localization(user_language_code).ERROR_DOCUMENT_FORBIDDEN,
            allow_sending_without_reply=True,
        )
