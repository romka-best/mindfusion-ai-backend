from datetime import datetime, timezone

from aiogram import Bot

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import Model, Quota, Currency, StableDiffusionVersion, FluxVersion
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
        category=ProductCategory.IMAGE,
        names={
            LanguageCode.RU: '🦄 Stable Diffusion XL',
            LanguageCode.EN: '🦄 Stable Diffusion XL',
            LanguageCode.ES: '🦄 Stable Diffusion XL',
            LanguageCode.HI: '🦄 Stable Diffusion XL',
        },
        descriptions={
            LanguageCode.RU: '🦄 Stable Diffusion XL',
            LanguageCode.EN: '🦄 Stable Diffusion XL',
            LanguageCode.ES: '🦄 Stable Diffusion XL',
            LanguageCode.HI: '🦄 Stable Diffusion XL',
        },
        prices={
            Currency.RUB: 4,
            Currency.USD: 0.04,
            Currency.XTR: 4,
        },
        order=2,
        details={
            'quota': Quota.STABLE_DIFFUSION_XL,
            'support_photos': True,
        },
    )
    await write_product(
        stripe_id='',
        is_active=True,
        type=ProductType.PACKAGE,
        category=ProductCategory.IMAGE,
        names={
            LanguageCode.RU: '🌲 Flux 1.0 Dev',
            LanguageCode.EN: '🌲 Flux 1.0 Dev',
            LanguageCode.ES: '🌲 Flux 1.0 Dev',
            LanguageCode.HI: '🌲 Flux 1.0 Dev',
        },
        descriptions={
            LanguageCode.RU: '🌲 Flux 1.0 Dev',
            LanguageCode.EN: '🌲 Flux 1.0 Dev',
            LanguageCode.ES: '🌲 Flux 1.0 Dev',
            LanguageCode.HI: '🌲 Flux 1.0 Dev',
        },
        prices={
            Currency.RUB: 4,
            Currency.USD: 0.04,
            Currency.XTR: 4,
        },
        order=4,
        details={
            'quota': Quota.FLUX_1_DEV,
            'support_photos': True,
        },
    )
    await write_product(
        stripe_id='',
        is_active=True,
        type=ProductType.PACKAGE,
        category=ProductCategory.IMAGE,
        names={
            LanguageCode.RU: '🐼 Recraft 3',
            LanguageCode.EN: '🐼 Recraft 3',
            LanguageCode.ES: '🐼 Recraft 3',
            LanguageCode.HI: '🐼 Recraft 3',
        },
        descriptions={
            LanguageCode.RU: '🐼 Recraft 3',
            LanguageCode.EN: '🐼 Recraft 3',
            LanguageCode.ES: '🐼 Recraft 3',
            LanguageCode.HI: '🐼 Recraft 3',
        },
        prices={
            Currency.RUB: 8,
            Currency.USD: 0.08,
            Currency.XTR: 8,
        },
        order=7,
        details={
            'quota': Quota.RECRAFT,
            'support_photos': False,
        },
    )

    await write_product(
        stripe_id='',
        is_active=True,
        type=ProductType.PACKAGE,
        category=ProductCategory.VIDEO,
        names={
            LanguageCode.RU: '🐇 Pika',
            LanguageCode.EN: '🐇 Pika',
            LanguageCode.ES: '🐇 Pika',
            LanguageCode.HI: '🐇 Pika',
        },
        descriptions={
            LanguageCode.RU: '🐇 Pika',
            LanguageCode.EN: '🐇 Pika',
            LanguageCode.ES: '🐇 Pika',
            LanguageCode.HI: '🐇 Pika',
        },
        prices={
            Currency.RUB: 75,
            Currency.USD: 0.75,
            Currency.XTR: 75,
        },
        order=3,
        details={
            'quota': Quota.PIKA,
            'support_photos': True,
        },
    )

    product_subscriptions = await get_active_products_by_product_type_and_category(ProductType.SUBSCRIPTION)
    for product_subscription in product_subscriptions:
        product_subscription.details['limits'][Quota.STABLE_DIFFUSION_XL] = \
            product_subscription.details['limits'][Quota.DALL_E]
        product_subscription.details['limits'][Quota.STABLE_DIFFUSION_3] = 0

        product_subscription.details['limits'][Quota.FLUX_1_DEV] = \
            product_subscription.details['limits'][Quota.DALL_E]
        product_subscription.details['limits'][Quota.FLUX_1_PRO] = 0

        product_subscription.details['limits'][Quota.RECRAFT] = 0

        product_subscription.details['limits'][Quota.PIKA] = 0

        product_subscription.details['limits'][Quota.WORK_WITH_FILES] = True

        try:
            del product_subscription.details['limits']['stable_diffusion']
        except KeyError:
            pass
        try:
            del product_subscription.details['limits']['flux']
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

            user.daily_limits[Quota.STABLE_DIFFUSION_XL] = \
                user.daily_limits[Quota.DALL_E]
            user.daily_limits[Quota.STABLE_DIFFUSION_3] = 0
            user.daily_limits[Quota.FLUX_1_DEV] = \
                user.daily_limits[Quota.DALL_E]
            user.daily_limits[Quota.FLUX_1_PRO] = 0
            user.daily_limits[Quota.RECRAFT] = \
                user.daily_limits[Quota.DALL_E]
            user.daily_limits[Quota.PIKA] = 0
            user.daily_limits[Quota.WORK_WITH_FILES] = True
            try:
                del user.daily_limits['stable_diffusion']
            except KeyError:
                pass
            try:
                del user.daily_limits['flux']
            except KeyError:
                pass

            user.additional_usage_quota[Quota.STABLE_DIFFUSION_XL] = 0
            user.additional_usage_quota[Quota.STABLE_DIFFUSION_3] = \
                user.additional_usage_quota.get('stable_diffusion', 0)
            user.additional_usage_quota[Quota.FLUX_1_DEV] = 0
            user.additional_usage_quota[Quota.FLUX_1_PRO] = \
                user.additional_usage_quota.get('flux', 0)
            user.additional_usage_quota[Quota.RECRAFT] = 0
            user.additional_usage_quota[Quota.PIKA] = 0
            user.additional_usage_quota[Quota.WORK_WITH_FILES] = True

            user.settings[Model.STABLE_DIFFUSION][UserSettings.VERSION] = StableDiffusionVersion.XL
            user.settings[Model.FLUX][UserSettings.VERSION] = FluxVersion.V1_Dev
            user.settings[Model.RECRAFT] = User.DEFAULT_SETTINGS[Model.RECRAFT]
            user.settings[Model.PIKA] = User.DEFAULT_SETTINGS[Model.PIKA]

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
