from bot.keyboards.photo_bundles.photos.delete_all_confirm import DeleteAllConfirm
from .base_handler import BaseHandler
from bot.database.operations.photo_bundle.photo_bundle import PhotoBundleGateway
from bot.keyboards import photo_bundles
from bot.states.common.photos_bundle import PhotoBundleState
import asyncio
from bot.helpers.photo_bundles.photo_binary_upload import PhotoBinaryUpload
from bot.database.models.photo_bundle.photo import Photo
from pathlib import Path
from bot.states.common.photos_bundle import PhotoBundleState
from .photo_bundles_handler import PhotoBundlesHandler
from bot.helpers.photo_bundles.photo_bundle_grid import PhotoBundleGrid
from bot.handlers.common.profile_handler import handle_profile

class PhotosHandler(BaseHandler):
    async def new(self):
        await self._delete_prev_media(prev_media_num=10)

        await self.state.set_state(PhotoBundleState.wait_new_photos)

        await self.message.answer(**photo_bundles.photos.New().render())

    async def create(self, album_msgs):
        [await msg.delete() for msg in album_msgs]

        # usecase
        ready_to_upload_photos = []

        new_photos_pool = [msg.photo[-1] for msg in album_msgs]
        saved_photos_pool = (
            await PhotoBundleGateway().get_by_user_id(self.message.chat.id)
        ).photos

        slots = dict.fromkeys(range(10))
        for saved_photo in saved_photos_pool:
            slots[saved_photo.id] = saved_photo

        for slot in slots.keys():
            if slots[slot] is None and len(new_photos_pool) > 0:
                ready_to_upload_photos.append([slot, new_photos_pool.pop()])

        tasks = []

        for index, photo in ready_to_upload_photos:

            async def task(photo=photo, index=index):
                file = await self.message.bot.get_file(photo.file_id)
                file_path = file.file_path
                file_io = await self.message.bot.download_file(file_path)

                return PhotoBinaryUpload(
                    Photo(index, photo.file_id, Path(
                        file_path).suffix.lstrip(".")),
                    file_io,
                )

            tasks.append(task())

        photo_uploads = await asyncio.gather(*tasks)

        await PhotoBundleGateway().save(self.message.from_user.id, photo_uploads)
        # /usecase

        await self.state.clear()
        await (
            await PhotoBundlesHandler.create_instance(self.message, self.state, delete_prev_msg=False)
        ).show()

        if len(new_photos_pool) > 0:
            await self.message.answer(
                text=f"Лимит фотографий достигнут, фотографий НЕ загружено — {len(new_photos_pool)}"
            )

    async def edit(self, photo_id, placeholder=False):
        await self._delete_prev_media(prev_media_num=10)

        await self.state.set_state(PhotoBundleState.wait_edit_photo)
        await self.state.update_data(photo_id=photo_id, is_placeholder=placeholder)

        await self.message.answer(**photo_bundles.photos.Edit().render())

    async def update(self, new_image):
        await self._delete_prev_media(prev_media_num=10)

        # usecase
        file = await self.message.bot.get_file(new_image.file_id)
        file_path = file.file_path
        file_io = await self.message.bot.download_file(file_path)

        data = await self.state.get_data()
        photo_id = data["photo_id"]
        is_placeholder = data["is_placeholder"]

        photo_upload = PhotoBinaryUpload(
            Photo(photo_id, new_image.file_id, Path(
                file_path).suffix.lstrip(".")),
            file_io,
        )
        if not is_placeholder:
            await PhotoBundleGateway().photo_update(
                self.message.from_user.id, photo_upload
            )
        else:
            await PhotoBundleGateway().save(self.message.from_user.id, [photo_upload])
        # /usecase

        await self.state.clear()
        await self.edit_mode()

    async def delete(self, photo_id):
        await self._delete_prev_media(prev_media_num=10)

        # usecase
        await PhotoBundleGateway().photo_delete_by_id(self.message.chat.id, photo_id)
        # /usecase

        await self.delete_mode()

    async def edit_mode(self):
        await self.state.clear()
        await self._delete_prev_media(prev_media_num=10)

        # usecase
        photo_bundle = await PhotoBundleGateway().get_by_user_id(self.message.chat.id)
        # /usecase

        grid = PhotoBundleGrid().build_grid(photo_bundle.photos)

        elements = photo_bundles.photos.EditMode().render(grid)

        await self.message.answer_media_group(media=elements["media"])
        await self.message.answer(
            text=elements["text"], reply_markup=elements["reply_markup"]
        )

    async def delete_mode(self):
        await self._delete_prev_media(prev_media_num=10)

        # usecase
        photo_bundle = await PhotoBundleGateway().get_by_user_id(self.message.chat.id)
        # /usecase

        grid = PhotoBundleGrid().build_grid(photo_bundle.photos)
        image_tg_ids = [photo.tg_id for photo in grid]
        image_ids = [photo.id for photo in photo_bundle.photos]

        elements = photo_bundles.photos.DeleteMode().render(image_tg_ids, image_ids)

        await self.message.answer_media_group(media=elements["media"])
        await self.message.answer(
            text=elements["text"], reply_markup=elements["reply_markup"]
        )

    async def delete_all_confirm(self):
        await self._delete_prev_media(prev_media_num=10)
        await self.message.answer(**DeleteAllConfirm().render())

    async def delete_all(self):
        # usecase
        await PhotoBundleGateway().photos_delete_all(self.message.chat.id)
        # /usecase

        await (
            await PhotoBundlesHandler.create_instance(
                self.message, self.state, delete_prev_msg=False
            )
        ).show()

    async def back_to_profile(self):
        await self._delete_prev_media(prev_media_num=10)
        await handle_profile(self.message, self.state, self.callback_query.from_user, False)
