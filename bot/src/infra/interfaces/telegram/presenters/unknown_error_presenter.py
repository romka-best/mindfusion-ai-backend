from bot.keyboards.common.common import build_error_keyboard
from bot.config import config, MessageSticker
from bot.locales.main import get_localization


class UnknownErrorPresenter:
    def __init__(self, lang_code, message):
        self.message = message
        self.lang_code = lang_code

    async def send_unknown_error_message(self):
        await self.message.answer_sticker(
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
        )

        await self.message.answer(
            text=get_localization(self.lang_code).ERROR,
            reply_markup=build_error_keyboard(self.lang_code),
        )
