# Copy me and rename to config_dev.py or config_dev_test.py or config_prod.py
from .message_effect import MessageEffect
from .message_sticker import MessageSticker


SUPER_ADMIN_ID = ""

MESSAGE_EFFECTS = {
    MessageEffect.FIRE:     "",  # 🔥
    MessageEffect.LIKE:     "",  # 👍
    MessageEffect.DISLIKE:  "",  # 👎
    MessageEffect.HEART:    "",  # ❤️
    MessageEffect.CONGRATS: "",  # 🎉
    MessageEffect.POOP:     "",  # 💩
}

MESSAGE_STICKERS = {
    MessageSticker.LOGO: "",
    MessageSticker.HELLO: "",
    MessageSticker.LOVE: "",
    MessageSticker.FEAR: "",
    MessageSticker.SAD: "",
    MessageSticker.THINKING: "",
    MessageSticker.CONNECTION_ERROR: "",
    MessageSticker.ERROR: "",
    MessageSticker.TEXT_GENERATION: "",
    MessageSticker.SUMMARY_GENERATION: "",
    MessageSticker.IMAGE_GENERATION: "",
    MessageSticker.MUSIC_GENERATION: "",
    MessageSticker.VIDEO_GENERATION: "",
}

BUNDLE_PHOTO_PLACEHOLDERS = {
    1: "",
    2: "",
    3: "",
    4: "",
    5: "",
    6: "",
    7: "",
    8: "",
    9: "",
    10: "",
}
