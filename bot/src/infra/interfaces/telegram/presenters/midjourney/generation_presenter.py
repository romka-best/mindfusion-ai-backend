from bot.config import config, MessageSticker
from bot.locales.main import get_localization
from bot.keyboards.ai.model import build_model_limit_exceeded_keyboard


class GenerationPresenter:
    def __init__(self, lang_code, message):
        self.message = message
        self.lang_code = lang_code

    async def send_image_processing_message(self):
        processing_sticker = await self.message.answer_sticker(
            sticker=config.MESSAGE_STICKERS.get(
                MessageSticker.IMAGE_GENERATION),
        )

        processing_message = await self.message.reply(
            text=get_localization(
                self.lang_code).model_image_processing_request(),
            allow_sending_without_reply=True,
        )

        return [processing_message, processing_sticker]

    async def send_model_limit_exceeded(self, user_had_subscription):
        await self.message.answer_sticker(
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
        )

        await self.message.reply(
            text=get_localization(self.lang_code).model_reached_usage_limit(),
            reply_markup=build_model_limit_exceeded_keyboard(
                self.lang_code, user_had_subscription),
            allow_sending_without_reply=True,
        )

    async def send_model_already_make_request(self):
        await self.message.reply(
            text=get_localization(self.lang_code).MODEL_ALREADY_MAKE_REQUEST,
            allow_sending_without_reply=True,
        )
