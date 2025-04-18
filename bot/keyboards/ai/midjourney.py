from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# from bot.database.models.common import MidjourneyVersion
# from bot.locales.main import get_localization
# from bot.locales.types import LanguageCode


def build_midjourney_keyboard(hash_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="U1", callback_data=f"midjourney:u1:{hash_id}"),
            InlineKeyboardButton(text="U2", callback_data=f"midjourney:u2:{hash_id}"),
            InlineKeyboardButton(text="U3", callback_data=f"midjourney:u3:{hash_id}"),
            InlineKeyboardButton(text="U4", callback_data=f"midjourney:u4:{hash_id}"),
        ],
        [
            InlineKeyboardButton(text="V1", callback_data=f"midjourney:v1:{hash_id}"),
            InlineKeyboardButton(text="V2", callback_data=f"midjourney:v2:{hash_id}"),
            InlineKeyboardButton(text="V3", callback_data=f"midjourney:v3:{hash_id}"),
            InlineKeyboardButton(text="V4", callback_data=f"midjourney:v4:{hash_id}"),
        ],
        [
            InlineKeyboardButton(
                text="🔄", callback_data=f"midjourney:again:{hash_id}"
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# def build_midjourney_image_keyboard(
#     language_code: LanguageCode,
#     hash_id: str,
#     version: MidjourneyVersion,
# ) -> InlineKeyboardMarkup:
#     buttons = []
#
#     if version == MidjourneyVersion.V5:
#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text=get_localization(language_code).UPSCALE_TWO,
#                     callback_data=f'midjourney_image:upscale_two:{hash_id}'
#                 ),
#                 InlineKeyboardButton(
#                     text=get_localization(language_code).UPSCALE_FOUR,
#                     callback_data=f'midjourney_image:upscale_four:{hash_id}'
#                 ),
#             ],
#         )
#     elif version == MidjourneyVersion.V6:
#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text=get_localization(language_code).UPSCALE_SUBTLE,
#                     callback_data=f'midjourney_image:upscale_subtle:{hash_id}'
#                 ),
#                 InlineKeyboardButton(
#                     text=get_localization(language_code).UPSCALE_CREATIVE,
#                     callback_data=f'midjourney_image:upscale_creative:{hash_id}'
#                 ),
#             ],
#         )
#
#     buttons.extend(
#         [
#             [
#                 InlineKeyboardButton(
#                     text=get_localization(language_code).VARY_SUBTLE,
#                     callback_data=f'midjourney_image:vary_subtle:{hash_id}'
#                 ),
#                 InlineKeyboardButton(
#                     text=get_localization(language_code).VARY_STRONG,
#                     callback_data=f'midjourney_image:vary_strong:{hash_id}'
#                 ),
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=get_localization(language_code).ZOOM_OUT_TWO,
#                     callback_data=f'midjourney_image:zoom_out_two:{hash_id}'
#                 ),
#                 InlineKeyboardButton(
#                     text=get_localization(language_code).ZOOM_OUT_ONE_AND_HALF,
#                     callback_data=f'midjourney_image:zoom_out_one_and_half:{hash_id}'
#                 ),
#             ],
#             [
#                 InlineKeyboardButton(
#                     text='⬅️',
#                     callback_data=f'midjourney_image:left:{hash_id}'
#                 ),
#                 InlineKeyboardButton(
#                     text='⬆️',
#                     callback_data=f'midjourney_image:top:{hash_id}'
#                 ),
#                 InlineKeyboardButton(
#                     text='➡️',
#                     callback_data=f'midjourney_image:right:{hash_id}'
#                 ),
#                 InlineKeyboardButton(
#                     text='⬇️',
#                     callback_data=f'midjourney_image:down:{hash_id}'
#                 ),
#             ]
#         ]
#     )
#
#     return InlineKeyboardMarkup(inline_keyboard=buttons)
