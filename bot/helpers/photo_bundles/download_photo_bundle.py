import asyncio
from bot.database.main import firebase
from bot.database.models.photo_bundle.photo_bundle import PhotoBundle
import zipfile
import io

class DownloadPhotoBundle:
    def __init__(self):
        self.bucket = firebase.bucket
        self.storage = firebase.storage

    async def execute(self, user_id: str, photo_bundle: PhotoBundle, output_zip=False):
        photo_ios = await asyncio.gather(
            *[
                self.storage.download(
                    self.bucket.name, f"users/avatars/{user_id}/{photo.file_name}"
                )
                for photo in photo_bundle.photos
            ]
        )

        if not output_zip:
            return photo_ios

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for index, photo in enumerate(photo_bundle.photos):
                zip_file.writestr(photo.file_name, photo_ios[index])

        return zip_buffer.getvalue()
