from aiogram import Router, F
from bot.middlewares.AlbumMiddleware import AlbumMiddleware
from .photos_handler import PhotosHandler
from .photo_bundles_handler import PhotoBundlesHandler
import re
from bot.states.common.photos_bundle import PhotoBundleState
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

photo_bundles_router = Router()
photo_bundles_router.message.middleware(AlbumMiddleware())


@photo_bundles_router.message(PhotoBundleState.wait_new_photos, F.photo)
async def handle_wait_new_photos(
    message: Message, state: FSMContext, album: list[Message] | None = None
):
    album_msgs = album if album else [message]
    await (
        await PhotosHandler.create_instance(message, state, delete_prev_msg=False)
    ).create(album_msgs)


@photo_bundles_router.message(PhotoBundleState.wait_edit_photo, F.photo)
async def handle_wait_edit_photo(message: Message, state: FSMContext):
    await (await PhotosHandler.create_instance(message, state)).update(
        message.photo[-1]
    )


@photo_bundles_router.callback_query(F.data == "photo_bundles:show")
async def handle_show(callback_query: CallbackQuery, state: FSMContext):
    await (
        await PhotoBundlesHandler.create_instance(callback_query.message, state)
    ).show()


@photo_bundles_router.callback_query(F.data == "photo_bundles:photos:new")
async def handle_new_photos(callback_query: CallbackQuery, state: FSMContext):
    await (await PhotosHandler.create_instance(callback_query.message, state)).new()


@photo_bundles_router.callback_query(F.data == "photo_bundles:photos:edit_mode")
async def handle_edit_mode(callback_query: CallbackQuery, state: FSMContext):
    await (
        await PhotosHandler.create_instance(callback_query.message, state)
    ).edit_mode()


@photo_bundles_router.callback_query(F.data == "photo_bundles:photos:delete_mode")
async def handle_delete_mode(callback_query: CallbackQuery, state: FSMContext):
    await (
        await PhotosHandler.create_instance(callback_query.message, state)
    ).delete_mode()


@photo_bundles_router.callback_query(
    F.data == "photo_bundles:photos:delete_all_confirm"
)
async def handle_delete_all_confirm(callback_query: CallbackQuery, state: FSMContext):
    await (
        await PhotosHandler.create_instance(callback_query.message, state)
    ).delete_all_confirm()


@photo_bundles_router.callback_query(F.data == "photo_bundles:photos:delete_all")
async def handle_delete_all(callback_query: CallbackQuery, state: FSMContext):
    await (
        await PhotosHandler.create_instance(callback_query.message, state)
    ).delete_all()


@photo_bundles_router.callback_query(
    F.data.regexp(r"^photo_bundles:photos:delete:(\d+)$")
)
async def handle_delete_photo(callback_query: CallbackQuery, state: FSMContext):
    photo_id = callback_query.data.split(":")[-1]
    await (await PhotosHandler.create_instance(callback_query.message, state)).delete(
        photo_id
    )


@photo_bundles_router.callback_query(
    F.data.regexp(r"^photo_bundles:photos:edit:(\d+)$")
)
async def handle_edit_photo(callback_query: CallbackQuery, state: FSMContext):
    photo_id = callback_query.data.split(":")[-1]
    await (await PhotosHandler.create_instance(callback_query.message, state)).edit(
        photo_id
    )


@photo_bundles_router.callback_query(
    F.data.regexp(r"^photo_bundles:photos:edit_placeholder:(\d+)$")
)
async def handle_edit_photo(callback_query: CallbackQuery, state: FSMContext):
    photo_id = callback_query.data.split(":")[-1]
    await (await PhotosHandler.create_instance(callback_query.message, state)).edit(
        photo_id, placeholder=True
    )

@photo_bundles_router.callback_query(F.data == "photo_bundles:back_to_profile")
async def handle_delete_all(callback_query: CallbackQuery, state: FSMContext):
    await (
        await PhotosHandler.create_instance(callback_query.message, state, callback_query=callback_query)
    ).back_to_profile()

