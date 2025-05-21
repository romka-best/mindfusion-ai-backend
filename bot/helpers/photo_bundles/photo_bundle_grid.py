from typing import List
from bot.database.models.photo_bundle.photo import Photo
from bot.database.models.photo_bundle.photo_placeholdeer import PhotoPlaceholder


class PhotoBundleGrid:
    def build_grid(self, photos: List[Photo]):
        photo_map = {photo.id: photo for photo in photos}
        grid = []

        for i in range(10):
            if i in photo_map:
                grid.append(photo_map[i])
            else:
                grid.append(PhotoPlaceholder(i + 1))

        return grid
