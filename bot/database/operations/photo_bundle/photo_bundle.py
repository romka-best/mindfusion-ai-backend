from bot.database.main import firebase
from pathlib import Path
from bot.database.models.photo_bundle.photo_bundle import PhotoBundle
from bot.database.models.photo_bundle.photo import Photo
import asyncio
from bot.helpers.photo_bundles.photo_binary_upload import PhotoBinaryUpload
from bot.database.operations.user.updaters import update_user


class PhotoBundleGateway:
    def __init__(self):
        self.bucket = firebase.bucket
        self.storage = firebase.storage

    async def __get_photo_blobs_list(self, user_id):
        photo_blobs_list = await self.bucket.list_blobs(
            prefix=f"users/avatars/{user_id}/"
        )
        return photo_blobs_list[1:]

    async def get_by_user_id(self, user_id: str):
        photo_blobs_list = await self.__get_photo_blobs_list(user_id)

        photos = []
        for photo_blob_path in photo_blobs_list:
            id_and_rg_id_part, file_format = Path(
                photo_blob_path).name.rsplit(".", 1)
            id, tg_id = id_and_rg_id_part.split("_", 1)

            photos.append(Photo(int(id), tg_id, file_format))

        return PhotoBundle(photos)

    async def save(self, user_id: str, photos: list[PhotoBinaryUpload]):
        await asyncio.gather(
            *[
                self.bucket.new_blob(
                    f"users/avatars/{user_id}/{photo.file_name}"
                ).upload(photo.file)
                for photo in photos
            ]
        )

        await update_user(str(user_id), {"face_swap_lora_version": ""})
        return PhotoBundle

    async def photos_delete_all(self, user_id):
        photo_blobs_list = await self.__get_photo_blobs_list(user_id)

        await asyncio.gather(
            *[
                self.storage.delete(bucket=self.bucket.name,
                                    object_name=blob_path)
                for blob_path in photo_blobs_list
            ]
        )

        await update_user(str(user_id), {"face_swap_lora_version": ""})

    async def photo_delete_by_id(self, user_id, id):
        object = await self.bucket.list_blobs(
            prefix=f"users/avatars/{user_id}/{id}_"
        )

        await self.storage.delete(bucket=self.bucket.name, object_name=object[0])
        await update_user(str(user_id), {"face_swap_lora_version": ""})

    async def photo_update(self, user_id, photo_upload):
        await self.photo_delete_by_id(user_id, photo_upload.id)
        await self.save(user_id, [photo_upload])
