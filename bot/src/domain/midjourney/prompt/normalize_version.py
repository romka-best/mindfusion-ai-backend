from bot.database.models.common import MidjourneyVersion


class NormalizeVersion:
    @staticmethod
    def execute(current_version, fallback_version=None):
        """
        Adjust midjourney version to our supported version, currently supported versions (5.2, 6.1)
        If passed unsupported version, fallback to 6.1
        Specify supported version important to calculate price
        """

        if not fallback_version:
            fallback_version = MidjourneyVersion.V6

        if current_version not in [MidjourneyVersion.V5, MidjourneyVersion.V6]:
            return fallback_version

        return current_version
