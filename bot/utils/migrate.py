from datetime import datetime, timezone

from aiogram import Bot

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import AspectRatio, Model, GeminiGPTVersion, RunwayVersion, RunwayResolution
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

            if user.settings[Model.GEMINI][UserSettings.VERSION] == 'gemini-2.0-pro-exp-02-05':
                user.settings[Model.GEMINI][UserSettings.VERSION] = GeminiGPTVersion.V2_Pro

            user.settings[Model.RUNWAY][UserSettings.VERSION] = RunwayVersion.V4_Turbo
            if user.settings[Model.RUNWAY][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE:
                user.settings[Model.RUNWAY][UserSettings.RESOLUTION] = RunwayResolution.LANDSCAPE
            else:
                user.settings[Model.RUNWAY][UserSettings.RESOLUTION] = RunwayResolution.PORTRAIT

            batch.update(user_ref, {
                'settings': user.settings,
                'edited_at': current_date,
            })

        await batch.commit()

        if count < config.BATCH_SIZE:
            is_running = False
            break

        last_doc = doc

    await send_message_to_admins_and_developers(bot, '<b>Database Migration Was Successful!</b> 🎉')
