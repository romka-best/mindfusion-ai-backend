from datetime import datetime, timezone

from aiogram.fsm.storage.base import BaseStorage

from bot.database.operations.transaction.getters import get_last_transaction_by_user

NOTIFICATION_INTERVALS = [1, 3, 7, 14, 30]


async def check_user_last_activity(
    user_id: str, created_at: datetime, storage: BaseStorage
) -> bool:
    current_date = datetime.now(timezone.utc)
    last_activity = await get_last_transaction_by_user(user_id)
    notification_stage = await get_notification_stage(user_id, storage)
    if last_activity:
        days_since_last_activity = (current_date - last_activity.created_at).days
        if days_since_last_activity <= 1 and notification_stage != 10:
            await set_notification_stage(user_id, 0, storage)
            return False

        if notification_stage < len(NOTIFICATION_INTERVALS):
            next_interval = NOTIFICATION_INTERVALS[notification_stage]
            if days_since_last_activity > next_interval:
                await set_notification_stage(user_id, notification_stage + 1, storage)
                return True
        return False
    else:
        days_since_registration = (current_date - created_at).days
        if notification_stage < len(NOTIFICATION_INTERVALS):
            next_interval = NOTIFICATION_INTERVALS[notification_stage]
            if days_since_registration > next_interval:
                await set_notification_stage(user_id, notification_stage + 1, storage)
                return True
        return False


async def set_notification_stage(
    user_id: str, notification_stage: int, storage: BaseStorage
):
    key = f"user:{user_id}:notification_stage"
    await storage.redis.set(key, notification_stage)


async def get_notification_stage(user_id: str, storage: BaseStorage) -> int:
    key = f"user:{user_id}:notification_stage"
    notification_stage = await storage.redis.get(key)
    if notification_stage is not None:
        notification_stage = int(notification_stage.decode())
        return notification_stage

    return 0
