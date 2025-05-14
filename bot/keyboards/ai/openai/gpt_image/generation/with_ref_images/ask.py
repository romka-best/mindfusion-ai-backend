from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.locales.main import get_localization


class Ask:
    def render(self, lang_code):
        return {
            "text": """
Отправьте до 10 референсных картинок 📸 в одном сообщении.

Промпт отправьте отдельным текстовым сообщением ✍️.
""",  # TODO loc
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
