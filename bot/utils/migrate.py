import logging
from datetime import datetime, timezone

from aiogram import Bot

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import Model, ClaudeGPTVersion
from bot.database.models.user import UserSettings, User
from bot.database.operations.user.getters import get_users
from bot.helpers.senders.send_message_to_admins import send_message_to_admins


async def migrate(bot: Bot):
    logging.info("START_MIGRATION")

    try:
        current_date = datetime.now(timezone.utc)

        users = await get_users()
        for i in range(0, len(users), config.USER_BATCH_SIZE):
            batch = firebase.db.batch()
            user_batch = users[i:i + config.USER_BATCH_SIZE]

            for user in user_batch:
                user_ref = firebase.db.collection(User.COLLECTION_NAME).document(user.id)

                if user.settings[Model.CLAUDE][UserSettings.VERSION] == 'claude-3-sonnet-20240229':
                    user.settings[Model.CLAUDE][UserSettings.VERSION] = ClaudeGPTVersion.V3_Sonnet

                    batch.update(user_ref, {
                        "interface_language_code": user.interface_language_code,
                        "currency": user.currency,
                        "settings": user.settings,
                        "edited_at": current_date,
                    })

            await batch.commit()

        await send_message_to_admins(bot, "<b>The database migration was successful!</b> 🎉")
    except Exception as e:
        logging.exception("Error in migration", e)
        await send_message_to_admins(bot, "<b>The database migration was not successful!</b> 🚨")
    finally:
        logging.info("END_MIGRATION")
