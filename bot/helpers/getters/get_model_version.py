from bot.database.models.common import (
    DALLEVersion,
    MidjourneyVersion,
    SunoVersion,
    KlingVersion,
    PikaVersion,
)
from bot.database.models.user import UserSettings


def get_model_version(model_settings: dict):
    if model_settings[UserSettings.VERSION] == DALLEVersion.V3:
        return '3'
    elif model_settings[UserSettings.VERSION] == SunoVersion.V3:
        return '3.5'
    elif model_settings[UserSettings.VERSION] == SunoVersion.V4:
        return '4.0'
    elif (
        model_settings[UserSettings.VERSION] == MidjourneyVersion.V5 or
        model_settings[UserSettings.VERSION] == MidjourneyVersion.V6 or
        model_settings[UserSettings.VERSION] == KlingVersion.V1 or
        model_settings[UserSettings.VERSION] == PikaVersion.V2
    ):
        return model_settings[UserSettings.VERSION]
