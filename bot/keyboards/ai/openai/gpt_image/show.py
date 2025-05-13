from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.locales.main import get_localization


class Show:
    def render(self, lang_code):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        #text=get_localization(lang_code).MODEL_CHANGE_AI,
                        text="Настройки",
                        callback_data="oai:gpt-image:settings:edit",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        #text=get_localization(lang_code).MODEL_CHANGE_AI,
                        text="Генерация по тексту",
                        callback_data="oai:gpt-image:gen:with_text_prompt:ask",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        #text=get_localization(lang_code).MODEL_CHANGE_AI,
                        text="Генерация на основе картинок",
                        callback_data="oai:gpt-image:gen:with_ref_images:ask",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        #text=get_localization(lang_code).MODEL_CHANGE_AI,
                        text="Назад к моделям",
                        callback_data="oai:gpt-image:back_to_models",
                    ),
                ],
            ],
        )
