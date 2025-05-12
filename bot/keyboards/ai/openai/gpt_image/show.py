from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.locales.main import get_localization


class Show:
    def render(self, lang_code):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_localization(lang_code).MODEL_SWITCHED_TO_AI_SETTINGS,
                        callback_data="oai:gpt-image:settings:edit",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(lang_code).ACTION_GENERATION_WITH_TEXT_PROMPT,
                        callback_data="oai:gpt-image:gen:with_text_prompt:ask_text_prompt",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(lang_code).ACTION_GENERATION_WITH_REF_IMAGES,
                        callback_data="oai:gpt-image:gen:with_ref_images:ask_photos",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(lang_code).ACTION_TO_OTHER_MODELS,
                        callback_data="oai:gpt-image:back_to_models",
                    ),
                ],
            ],
        )
