from aiogram import Router, F
from bot.middlewares.AlbumMiddleware import AlbumMiddleware
from .photos_handler import PhotosHandler
from .photo_bundles_handler import PhotoBundlesHandler
from bot.states.common.photos_bundle import PhotoBundleState
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.utils.with_user_language import with_user_language

photo_bundles_router = Router()
photo_bundles_router.message.middleware(AlbumMiddleware())


@photo_bundles_router.message(PhotoBundleState.wait_new_photos, F.photo)
@with_user_language
async def handle_wait_new_photos(
    message: Message,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    album: list[Message] | None = None,
    delete_prev_msgs_num=0,
):
    album_msgs = album if album else [message]
    await (
        await PhotosHandler.create_instance(
            message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).create(album_msgs)


@photo_bundles_router.message(PhotoBundleState.wait_edit_photo, F.photo)
@with_user_language
async def handle_wait_edit_photo(
    message: Message,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
    album: list[Message] | None = None,
):
    album_msgs = album if album else [message]
    await (
        await PhotosHandler.create_instance(
            message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).update(album_msgs)


@photo_bundles_router.callback_query(F.data == "photo_bundles:show")
@with_user_language
async def handle_show(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    await (
        await PhotoBundlesHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).show()


@photo_bundles_router.callback_query(F.data == "photo_bundles:photos:new")
@with_user_language
async def handle_new_photos(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).new()


@photo_bundles_router.callback_query(F.data == "photo_bundles:photos:edit_mode")
@with_user_language
async def handle_edit_mode(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).edit_mode()


@photo_bundles_router.callback_query(F.data == "photo_bundles:photos:delete_mode")
@with_user_language
async def handle_delete_mode(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).delete_mode()


@photo_bundles_router.callback_query(
    F.data == "photo_bundles:photos:delete_all_confirm"
)
@with_user_language
async def handle_delete_all_confirm(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).delete_all_confirm()


@photo_bundles_router.callback_query(
    F.data.regexp(r"^photo_bundles:photos:delete:(\d+)$")
)
@with_user_language
async def handle_delete_photo(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    photo_id = callback_query.data.split(":")[-1]
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).delete(photo_id)


@photo_bundles_router.callback_query(
    F.data.regexp(r"^photo_bundles:photos:edit_placeholder:(\d+)$")
)
@with_user_language
async def handle_edit_photo_placeholder(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    photo_id = callback_query.data.split(":")[-1]
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).edit(photo_id, placeholder=True)


@photo_bundles_router.callback_query(
    F.data.regexp(r"^photo_bundles:photos:edit:(\d+)$")
)
@with_user_language
async def handle_edit_photo(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    photo_id = callback_query.data.split(":")[-1]
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).edit(photo_id)


@photo_bundles_router.callback_query(F.data == "photo_bundles:back_to_profile")
@with_user_language
async def handle_back_to_profile(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            callback_query=callback_query,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).back_to_profile()


@photo_bundles_router.callback_query(F.data == "photo_bundles:photos:delete_all")
@with_user_language
async def handle_delete_all(
    callback_query: CallbackQuery,
    state: FSMContext,
    lang_code: str,
    user_id: int,
    delete_prev_msgs_num=0,
):
    await (
        await PhotosHandler.create_instance(
            callback_query.message,
            state,
            lang_code,
            user_id,
            delete_prev_msgs_num=delete_prev_msgs_num,
        )
    ).delete_all()
