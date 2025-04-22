from aiogram.types import InputMediaPhoto


class Gallery:
    def render(self, media: list):
        return {"media": [InputMediaPhoto(media=m) for m in media]}
