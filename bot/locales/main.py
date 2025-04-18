from typing import Type

from aiogram.fsm.storage.base import BaseStorage

from ..database.operations.user.updaters import update_user
from . import en, es, hi, ru
from .texts import Texts
from .types import LanguageCode

localization_classes: dict[LanguageCode, Type[Texts]] = {
    LanguageCode.EN: en.English,
    LanguageCode.RU: ru.Russian,
    LanguageCode.ES: es.Spanish,
    LanguageCode.HI: hi.Hindi,
}


async def set_user_language(
    user_id: str, language_code: LanguageCode, storage: BaseStorage
):
    if language_code not in localization_classes.keys():
        language_code = LanguageCode.EN

    key = f"user:{user_id}:language"
    await storage.redis.set(key, language_code)

    await update_user(
        user_id,
        {
            "interface_language_code": language_code,
        },
    )

    return language_code


async def get_user_language(user_id: str, storage: BaseStorage) -> LanguageCode:
    key = f"user:{user_id}:language"
    language_code = await storage.redis.get(key)
    if language_code is not None:
        language_code = language_code.decode()

    if language_code not in localization_classes.keys():
        return LanguageCode.EN

    return language_code


def get_localization(language_code: LanguageCode) -> Texts:
    localization_class = localization_classes.get(language_code, en.English)
    return localization_class()
