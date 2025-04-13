from bot.database.models.common import Quota


class MidjourneyUserQuotaService:
    def __init__(self, user):
        self.user = user

    def calculate(self):
        return (
            self.user.daily_limits[Quota.MIDJOURNEY]
            + self.user.additional_usage_quota[Quota.MIDJOURNEY]
        )

    def is_quota_enough(self):
        return self.calculate() >= 1
