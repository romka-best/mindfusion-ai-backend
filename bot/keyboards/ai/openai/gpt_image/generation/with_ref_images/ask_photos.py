from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.locales.main import get_localization


class AskPhotos:
    def render(self, lang_code):
        return {
            "text": get_localization(lang_code).ask_ref_images(10),
            "reply_markup": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=get_localization(lang_code).ACTION_CANCEL, callback_data="oai:gpt-image:show",
                        ),
                    ],
                ],
            ),
        }
