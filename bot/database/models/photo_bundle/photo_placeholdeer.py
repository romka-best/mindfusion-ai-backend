from bot.config import config

class PhotoPlaceholder:
    def __init__(self, placeholder_num):
        self.tg_id = config.BUNDLE_PHOTO_PLACEHOLDERS[placeholder_num]
