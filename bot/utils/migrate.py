from datetime import datetime, timezone

from aiogram import Bot

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import Model, Quota, ChatGPTVersion, Currency
from bot.database.models.product import ProductType, ProductCategory
from bot.database.models.user import User, UserSettings
from bot.database.operations.product.getters import get_active_products_by_product_type_and_category
from bot.database.operations.product.updaters import update_product
from bot.database.operations.product.writers import write_product
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers
from bot.locales.types import LanguageCode


async def migrate(bot: Bot):
    current_date = datetime.now(timezone.utc)

    await write_product(
        stripe_id='',
        is_active=True,
        type=ProductType.PACKAGE,
        category=ProductCategory.TEXT,
        names={
            LanguageCode.RU: '👽 ChatGPT 4.1 Mini',
            LanguageCode.EN: '👽 ChatGPT 4.1 Mini',
            LanguageCode.ES: '👽 ChatGPT 4.1 Mini',
            LanguageCode.HI: '👽 ChatGPT 4.1 Mini',
        },
        descriptions={
            LanguageCode.RU: '👽 ChatGPT 4.1 Mini',
            LanguageCode.EN: '👽 ChatGPT 4.1 Mini',
            LanguageCode.ES: '👽 ChatGPT 4.1 Mini',
            LanguageCode.HI: '👽 ChatGPT 4.1 Mini',
        },
        prices={
            Currency.RUB: 1,
            Currency.USD: 0.01,
            Currency.XTR: 1,
        },
        order=4,
        details={
            'quota': Quota.CHAT_GPT_4_1_MINI,
            'support_photos': True,
            'support_documents': True,
        },
    )
    await write_product(
        stripe_id='',
        is_active=True,
        type=ProductType.PACKAGE,
        category=ProductCategory.TEXT,
        names={
            LanguageCode.RU: '🛸 ChatGPT 4.1',
            LanguageCode.EN: '🛸 ChatGPT 4.1',
            LanguageCode.ES: '🛸 ChatGPT 4.1',
            LanguageCode.HI: '🛸 ChatGPT 4.1',
        },
        descriptions={
            LanguageCode.RU: '🛸 ChatGPT 4.1',
            LanguageCode.EN: '🛸 ChatGPT 4.1',
            LanguageCode.ES: '🛸 ChatGPT 4.1',
            LanguageCode.HI: '🛸 ChatGPT 4.1',
        },
        prices={
            Currency.RUB: 4,
            Currency.USD: 0.04,
            Currency.XTR: 4,
        },
        order=5,
        details={
            'quota': Quota.CHAT_GPT_4_1,
            'support_photos': True,
            'support_documents': True,
        },
    )

    product_subscriptions = await get_active_products_by_product_type_and_category(ProductType.SUBSCRIPTION)
    for product_subscription in product_subscriptions:
        product_subscription.details['limits'][Quota.CHAT_GPT_O_3] = \
            product_subscription.details['limits']['o1']
        product_subscription.details['limits'][Quota.CHAT_GPT_O_4_MINI] = \
            product_subscription.details['limits']['o3-mini']

        try:
            del product_subscription.details['limits']['o1']
        except KeyError:
            pass

        try:
            del product_subscription.details['limits']['o3-mini']
        except KeyError:
            pass

        product_subscription.details['limits'][Quota.CHAT_GPT_4_1] = \
            product_subscription.details['limits'][Quota.CHAT_GPT4_OMNI]
        product_subscription.details['limits'][Quota.CHAT_GPT_4_1_MINI] = \
            product_subscription.details['limits'][Quota.CHAT_GPT4_OMNI_MINI]

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

            user.daily_limits[Quota.CHAT_GPT_O_3] = user.daily_limits.get('o1', 0)
            user.daily_limits[Quota.CHAT_GPT_O_4_MINI] = user.daily_limits.get('o3-mini', 0)
            user.daily_limits[Quota.CHAT_GPT_4_1] = user.daily_limits[Quota.CHAT_GPT4_OMNI]
            user.daily_limits[Quota.CHAT_GPT_4_1_MINI] = user.daily_limits[Quota.CHAT_GPT4_OMNI_MINI]

            try:
                del user.daily_limits['o1']
            except KeyError:
                pass

            try:
                del user.daily_limits['o3-mini']
            except KeyError:
                pass

            user.additional_usage_quota[Quota.CHAT_GPT_O_3] = user.additional_usage_quota.get('o1', 0)
            user.additional_usage_quota[Quota.CHAT_GPT_O_4_MINI] = user.additional_usage_quota.get('o3-mini', 0)
            user.additional_usage_quota[Quota.CHAT_GPT_4_1] = 0
            user.additional_usage_quota[Quota.CHAT_GPT_4_1_MINI] = 0

            try:
                del user.additional_usage_quota['o1']
            except KeyError:
                pass

            try:
                del user.additional_usage_quota['o3-mini']
            except KeyError:
                pass

            if user.settings[Model.CHAT_GPT][UserSettings.VERSION] == 'o1':
                user.settings[Model.CHAT_GPT][UserSettings.VERSION] = ChatGPTVersion.V3_O
            elif user.settings[Model.CHAT_GPT][UserSettings.VERSION] == 'o3-mini':
                user.settings[Model.CHAT_GPT][UserSettings.VERSION] = ChatGPTVersion.V4_O_Mini

            batch.update(user_ref, {
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
