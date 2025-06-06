from bot.database.operations.photo_bundle.photo_bundle import PhotoBundleGateway
from ..base_handler import BaseHandler
from bot.keyboards import photo_bundles
from bot.helpers.photo_bundles.photo_bundle_grid import PhotoBundleGrid


class PhotoBundlesHandler(BaseHandler):
    async def show(self):
        # usecase
        photo_bundle = await PhotoBundleGateway().get_by_user_id(self.user_id)
        grid = PhotoBundleGrid().build_grid(photo_bundle.photos)
        image_tg_ids = [photo.tg_id for photo in grid]
        # /usecase

        if image_tg_ids:
            await self.message.answer_media_group(
                **photo_bundles.Gallery().render(image_tg_ids)
            )

        await self.message.answer(**photo_bundles.Show().render(self.lang_code))
