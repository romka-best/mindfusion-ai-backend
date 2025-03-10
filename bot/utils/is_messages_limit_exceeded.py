from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import config, MessageSticker
from bot.database.models.common import Model, Quota
from bot.database.models.subscription import SUBSCRIPTION_FREE_LIMITS
from bot.database.models.user import User, UserSettings
from bot.database.operations.product.getters import get_product, get_product_by_quota
from bot.database.operations.subscription.getters import get_subscription
from bot.integrations.kling import Kling
from bot.integrations.luma import get_cost_for_video as get_cost_for_luma_ray_video
from bot.integrations.open_ai import get_cost_for_image
from bot.integrations.runway import get_cost_for_video as get_cost_for_runway_video
from bot.keyboards.ai.model import build_model_limit_exceeded_keyboard, build_model_restricted_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode


async def is_messages_limit_exceeded(message: Message, state: FSMContext, user: User, user_quota: Quota):
    generation_cost = 1
    if user.current_model == Model.DALL_E:
        generation_cost = get_cost_for_image(
            user.settings[Model.DALL_E][UserSettings.QUALITY],
            user.settings[Model.DALL_E][UserSettings.RESOLUTION],
        )
    elif user.current_model == Model.KLING:
        generation_cost = Kling.get_cost_for_video(
            user.settings[Model.KLING][UserSettings.MODE],
            user.settings[Model.KLING][UserSettings.DURATION],
        )
    elif user.current_model == Model.RUNWAY:
        generation_cost = get_cost_for_runway_video(
            user.settings[Model.RUNWAY][UserSettings.DURATION],
        )
    elif user.current_model == Model.LUMA_RAY:
        generation_cost = get_cost_for_luma_ray_video(
            user.settings[Model.LUMA_RAY][UserSettings.QUALITY],
            user.settings[Model.LUMA_RAY][UserSettings.DURATION],
        )

    max_generations = user.daily_limits[user_quota] + user.additional_usage_quota[user_quota]

    if max_generations < generation_cost:
        user_language_code = await get_user_language(user.id, state.storage)

        await message.answer_sticker(
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
        )

        if user.subscription_id:
            user_subscription = await get_subscription(user.subscription_id)
            product_subscription = await get_product(user_subscription.product_id)
            subscription_limits = product_subscription.details.get('limits', SUBSCRIPTION_FREE_LIMITS)
        else:
            subscription_limits = SUBSCRIPTION_FREE_LIMITS

        if subscription_limits.get(user_quota) == 0:
            product = await get_product_by_quota(user_quota)
            product_name = product.names.get(user_language_code) or product.names.get(LanguageCode.EN)
            await message.reply(
                text=get_localization(user_language_code).model_restricted(product_name),
                reply_markup=build_model_restricted_keyboard(user_language_code, user.had_subscription),
                allow_sending_without_reply=True,
            )
        else:
            await message.reply(
                text=get_localization(user_language_code).model_reached_usage_limit(),
                reply_markup=build_model_limit_exceeded_keyboard(user_language_code, user.had_subscription),
                allow_sending_without_reply=True,
            )

        return True

    return False
