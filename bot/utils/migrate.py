from datetime import datetime, timezone

from aiogram import Bot

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import Model, Quota, ChatGPTVersion
from bot.database.models.product import ProductType
from bot.database.models.user import User, UserSettings
from bot.database.operations.product.getters import get_active_products_by_product_type_and_category
from bot.database.operations.product.updaters import update_product
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers


async def migrate(bot: Bot):
    current_date = datetime.now(timezone.utc)

    product_subscriptions = await get_active_products_by_product_type_and_category(ProductType.SUBSCRIPTION)
    for product_subscription in product_subscriptions:
        product_subscription.details['limits'][Quota.CHAT_GPT_O_3_MINI] = \
            product_subscription.details['limits'][Quota.CHAT_GPT4_OMNI]

        try:
            del product_subscription.details['limits']['o1_mini']
        except KeyError:
            pass

        await update_product(product_subscription.id, {
            'details': product_subscription.details,
            'edited_at': current_date,
        })

    users_query = firebase.db.collection(User.COLLECTION_NAME).limit(config.BATCH_SIZE)
    is_running = True
    last_doc = None

    while is_running:
        if last_doc:
            users_query = users_query.start_after(last_doc)

        docs = users_query.stream()

        batch = firebase.db.batch()

        count = 0
        async for doc in docs:
            count += 1

            user = User(**doc.to_dict())

            user_ref = firebase.db.collection(User.COLLECTION_NAME).document(user.id)

            user.daily_limits[Quota.CHAT_GPT_O_3_MINI] = user.daily_limits[Quota.CHAT_GPT4_OMNI]
            try:
                del user.daily_limits['o1_mini']
            except KeyError:
                pass

            user.additional_usage_quota[Quota.CHAT_GPT_O_3_MINI] = user.additional_usage_quota.get('o1_mini', 0)
            try:
                del user.additional_usage_quota['o1_mini']
            except KeyError:
                pass

            if user.settings[Model.CHAT_GPT][UserSettings.VERSION] == 'o1-mini':
                user.settings[Model.CHAT_GPT][UserSettings.VERSION] = ChatGPTVersion.V3_O_Mini

            batch.update(user_ref, {
                'daily_limits': user.daily_limits,
                'additional_usage_quota': user.additional_usage_quota,
                'settings': user.settings,
                'edited_at': current_date,
            })

        await batch.commit()

        if count < config.BATCH_SIZE:
            is_running = False
            break

        last_doc = doc

    await send_message_to_admins_and_developers(bot, '<b>Database Migration Was Successful!</b> 🎉')
