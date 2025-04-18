from datetime import datetime, timezone
from typing import cast

from babel.dates import format_date

from bot.database.models.common import ModelType, Quota
from bot.database.models.user import User
from bot.database.operations.chat.getters import get_chat
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.role.getters import get_role
from bot.helpers.getters.get_model_type import get_model_type
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


async def get_switched_to_ai_model(
    user: User, quota: Quota, language_code: LanguageCode
):
    product = await get_product_by_quota(quota)

    role_info = {}
    model_type = get_model_type(user.current_model)
    if model_type == ModelType.TEXT:
        chat = await get_chat(user.current_chat_id)
        role = await get_role(chat.role_id)
        role_info = {
            "role": role.translated_names.get(language_code)
            or role.translated_names.get(LanguageCode.EN)
        }

    current_date = datetime.now(timezone.utc)
    training_data = product.details.get("training_data", current_date)
    formatted_date = format_date(
        date=training_data, format="LLLL, yyyy", locale=language_code
    ).capitalize()
    product.details["training_data"] = formatted_date

    product_info = product.details
    settings_info = user.settings[user.current_model]

    model_name = product.names.get(language_code) or product.names.get(LanguageCode.EN)
    model_type = cast(ModelType, product.category)
    model_info = product_info | role_info | settings_info

    text = get_localization(language_code).model_switched(
        model_name,
        model_type,
        model_info,
    )

    return text
