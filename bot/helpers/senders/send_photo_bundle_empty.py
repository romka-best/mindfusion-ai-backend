from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from bot.locales.main import get_localization


async def send_photo_bundle_empty(message, lang_code):
    await message.answer(
        text=get_localization(lang_code).error_photo_bundle_empty(),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_localization(lang_code).menu_bundle_photo_managment(),
                        callback_data="photo_bundles:show",
                    ),
                ],
            ]
        ),
    )
