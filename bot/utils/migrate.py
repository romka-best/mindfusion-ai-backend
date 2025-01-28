from datetime import datetime, timezone

from aiogram import Bot

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import Model, Quota, Currency
from bot.database.models.product import ProductType, ProductCategory
from bot.database.models.user import User
from bot.database.operations.product.getters import get_active_products_by_product_type_and_category
from bot.database.operations.product.updaters import update_product
from bot.database.operations.product.writers import write_product
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers
from bot.locales.types import LanguageCode


async def migrate(bot: Bot):
    current_date = datetime.now(timezone.utc)

    await write_product(
        stripe_id='prod_RfS0UAqz5ZoOyh',
        is_active=True,
        type=ProductType.PACKAGE,
        category=ProductCategory.TEXT,
        names={
            LanguageCode.RU: '🐬 DeepSeek V3',
            LanguageCode.EN: '🐬 DeepSeek V3',
            LanguageCode.ES: '🐬 DeepSeek V3',
            LanguageCode.HI: '🐬 DeepSeek V3',
        },
        descriptions={
            LanguageCode.RU: '🐬 DeepSeek V3',
            LanguageCode.EN: '🐬 DeepSeek V3',
            LanguageCode.ES: '🐬 DeepSeek V3',
            LanguageCode.HI: '🐬 DeepSeek V3',
        },
        prices={
            Currency.RUB: 1,
            Currency.USD: 0.01,
            Currency.XTR: 1,
        },
        order=11,
        details={
            'quota': Quota.DEEP_SEEK_V3,
            'support_photos': False,
            'support_documents': False,
        },
    )
    await write_product(
        stripe_id='prod_RfS0IdUZCJC52o',
        is_active=True,
        type=ProductType.PACKAGE,
        category=ProductCategory.TEXT,
        names={
            LanguageCode.RU: '🐋 DeepSeek R1',
            LanguageCode.EN: '🐋 DeepSeek R1',
            LanguageCode.ES: '🐋 DeepSeek R1',
            LanguageCode.HI: '🐋 DeepSeek R1',
        },
        descriptions={
            LanguageCode.RU: '🐋 DeepSeek R1',
            LanguageCode.EN: '🐋 DeepSeek R1',
            LanguageCode.ES: '🐋 DeepSeek R1',
            LanguageCode.HI: '🐋 DeepSeek R1',
        },
        prices={
            Currency.RUB: 4,
            Currency.USD: 0.04,
            Currency.XTR: 4,
        },
        order=12,
        details={
            'quota': Quota.DEEP_SEEK_R1,
            'support_photos': False,
            'support_documents': False,
        },
    )

    product_subscriptions = await get_active_products_by_product_type_and_category(ProductType.SUBSCRIPTION)
    for product_subscription in product_subscriptions:
        product_subscription.details['limits'][Quota.DEEP_SEEK_V3] = \
            product_subscription.details['limits'][Quota.CHAT_GPT4_OMNI_MINI]
        product_subscription.details['limits'][Quota.DEEP_SEEK_R1] = \
            product_subscription.details['limits'][Quota.CHAT_GPT4_OMNI]

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

            user.daily_limits[Quota.DEEP_SEEK_V3] = user.daily_limits[Quota.CHAT_GPT4_OMNI_MINI]
            user.daily_limits[Quota.DEEP_SEEK_R1] = user.daily_limits[Quota.CHAT_GPT4_OMNI]

            user.additional_usage_quota[Quota.DEEP_SEEK_V3] = 0
            user.additional_usage_quota[Quota.DEEP_SEEK_R1] = 0

            user.settings[Model.LUMA_RAY] = User.DEFAULT_SETTINGS[Model.LUMA_RAY]
            user.settings[Model.DEEP_SEEK] = User.DEFAULT_SETTINGS[Model.DEEP_SEEK]

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
