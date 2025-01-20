from datetime import datetime, timezone

from aiogram import Bot

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import Currency, Quota
from bot.database.models.product import ProductType, ProductCategory
from bot.database.models.user import User
from bot.database.operations.product.writers import write_product
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers
from bot.locales.types import LanguageCode


async def migrate(bot: Bot):
    current_date = datetime.now(timezone.utc)

    await write_product(
        stripe_id='prod_RcV3U1CM0arQax',
        is_active=True,
        type=ProductType.PACKAGE,
        category=ProductCategory.OTHER,
        names={
            LanguageCode.RU: '📷 Работа с фото/документами',
            LanguageCode.EN: '📷 Working with photos/documents',
            LanguageCode.ES: '📷 Trabajo con fotos/documentos',
            LanguageCode.HI: '📷 फोटो/दस्तावेज़ के साथ काम करें',
        },
        descriptions={
            LanguageCode.RU: '📷 Работа с фото/документами',
            LanguageCode.EN: '📷 Working with photos/documents',
            LanguageCode.ES: '📷 Trabajo con fotos/documentos',
            LanguageCode.HI: '📷 फोटो/दस्तावेज़ के साथ काम करें',
        },
        prices={
            Currency.RUB: 50,
            Currency.USD: 0.50,
            Currency.XTR: 50,
        },
        order=0,
        details={
            'quota': Quota.WORK_WITH_FILES,
            'is_recurring': True,
        },
    )

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

            if not user.subscription_id:
                user.daily_limits[Quota.WORK_WITH_FILES] = False
            user.additional_usage_quota[Quota.WORK_WITH_FILES] = False

            batch.update(user_ref, {
                'daily_limits': user.daily_limits,
                'additional_usage_quota': user.additional_usage_quota,
                'edited_at': current_date,
            })

        await batch.commit()

        if count < config.BATCH_SIZE:
            is_running = False
            break

        last_doc = doc

    await send_message_to_admins_and_developers(bot, '<b>Database Migration Was Successful!</b> 🎉')
