from datetime import datetime, timezone

from aiogram import Bot

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import Model, ClaudeGPTVersion
from bot.database.models.user import User, UserSettings
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers


async def migrate(bot: Bot):
    current_date = datetime.now(timezone.utc)

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

            if user.subscription_id:
                user.had_subscription = True
            else:
                user.had_subscription = False

            if user.settings[Model.CLAUDE][UserSettings.VERSION] == 'claude-3-5-sonnet-latest':
                user.settings[Model.CLAUDE][UserSettings.VERSION] = ClaudeGPTVersion.V3_Sonnet

            batch.update(user_ref, {
                'had_subscription': user.had_subscription,
                'settings': user.settings,
                'edited_at': current_date,
            })

        await batch.commit()

        if count < config.BATCH_SIZE:
            is_running = False
            break

        last_doc = doc

    await send_message_to_admins_and_developers(bot, '<b>Database Migration Was Successful!</b> 🎉')
