from datetime import datetime, timedelta, timezone


def get_time_until_limit_update(hours=6):
    current_date = datetime.now(timezone.utc)
    update_date = datetime(
        current_date.year, current_date.month, current_date.day, tzinfo=timezone.utc
    ) + timedelta(days=1, hours=hours)
    time_left = update_date - current_date
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes = remainder // 60

    return hours, minutes
