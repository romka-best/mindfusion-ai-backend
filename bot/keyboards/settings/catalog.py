from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton

from bot.database.models.common import Model, ModelType
from bot.database.models.prompt import Prompt, PromptCategory, PromptSubCategory
from bot.database.models.role import Role
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_catalog_keyboard(language_code: LanguageCode):
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CATALOG_DIGITAL_EMPLOYEES,
                callback_data=f'catalog:digital_employees'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).CATALOG_PROMPTS,
                callback_data=f'catalog:prompts'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_catalog_digital_employees_keyboard(
    language_code: LanguageCode,
    current_role_id: str,
    roles: list[Role],
    model: Optional[Model] = None,
    from_settings=False,
) -> InlineKeyboardMarkup:
    buttons = []
    for role in roles:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=role.translated_names.get(language_code) + (
                        ' ✅' if current_role_id == role.id else ''
                    ),
                    callback_data=f'catalog_digital_employees:{role.id}'
                )
            ],
        )
    buttons.append([
        InlineKeyboardButton(
            text=get_localization(language_code).ACTION_BACK,
            callback_data=f'catalog_digital_employees:back:{from_settings}:{model}' if model else f'catalog_digital_employees:back:{from_settings}'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_catalog_prompts_model_type_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_TEXT,
                callback_data=f'catalog_prompts_model_type:{ModelType.TEXT}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_IMAGE,
                callback_data=f'catalog_prompts_model_type:{ModelType.IMAGE}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_MUSIC,
                callback_data=f'catalog_prompts_model_type:{ModelType.MUSIC}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f'catalog_prompts_model_type:back'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_catalog_prompt_categories_keyboard(
    language_code: LanguageCode,
    categories: list[PromptCategory],
    has_close_button: bool = False,
) -> InlineKeyboardMarkup:
    buttons = []
    for category in categories:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=category.names.get(language_code),
                    callback_data=f'catalog_prompt_category:{category.id}'
                )
            ],
        )

    if has_close_button:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CLOSE,
                callback_data=f'catalog_prompt_category:close'
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f'catalog_prompt_category:back'
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_catalog_prompt_subcategories_keyboard(
    language_code: LanguageCode,
    subcategories: list[PromptSubCategory],
) -> InlineKeyboardMarkup:
    buttons = []
    for subcategory in subcategories:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=subcategory.names.get(language_code),
                    callback_data=f'catalog_prompt_subcategory:{subcategory.id}'
                )
            ],
        )
    buttons.append([
        InlineKeyboardButton(
            text=get_localization(language_code).ACTION_BACK,
            callback_data=f'catalog_prompt_subcategory:back'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_prompts_catalog_keyboard(
    language_code: LanguageCode,
    prompts: list[Prompt],
) -> InlineKeyboardMarkup:
    buttons = []
    buttons_row = []
    for index, prompt in enumerate(prompts):
        emoji_number = ''.join(f'{digit}\uFE0F\u20E3' for digit in str(index + 1))
        buttons_row.append(
            InlineKeyboardButton(
                text=emoji_number,
                callback_data=f'catalog_prompt:{prompt.id}'
            )
        )

        if len(buttons_row) == 2:
            buttons.append(buttons_row)
            buttons_row = []

    if buttons_row:
        buttons.append(buttons_row)

    buttons.append([
        InlineKeyboardButton(
            text=get_localization(language_code).ACTION_BACK,
            callback_data=f'catalog_prompt:back'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_prompts_catalog_chosen_keyboard(
    language_code: LanguageCode,
    prompt: Prompt,
) -> InlineKeyboardMarkup:
    buttons = []

    if prompt.short_prompts.get(language_code):
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).CATALOG_PROMPTS_GET_SHORT_PROMPT,
                callback_data=f'catalog_prompt_chosen:short:{prompt.id}'
            )
        ])
    if prompt.long_prompts.get(language_code):
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).CATALOG_PROMPTS_GET_LONG_PROMPT,
                callback_data=f'catalog_prompt_chosen:long:{prompt.id}'
            )
        ])
    if prompt.has_examples:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).CATALOG_PROMPTS_GET_EXAMPLES,
                callback_data=f'catalog_prompt_chosen:examples:{prompt.id}'
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text=get_localization(language_code).ACTION_BACK,
            callback_data=f'catalog_prompt_chosen:back'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_prompts_catalog_copy_keyboard(
    language_code: LanguageCode,
    prompt_text: str,
) -> InlineKeyboardMarkup:
    buttons = []

    if len(prompt_text) < 256:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).CATALOG_PROMPTS_COPY,
                copy_text=CopyTextButton(
                    text=prompt_text,
                ),
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text=get_localization(language_code).ACTION_BACK,
            callback_data=f'catalog_prompt_info_chosen:back'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
