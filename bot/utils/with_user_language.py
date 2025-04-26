from functools import wraps
from bot.locales.main import get_user_language
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery


def with_user_language(handler):
    @wraps(handler)
    async def wrapper(*args, **kwargs):
        message_or_query = next(
            (arg for arg in args if isinstance(arg, (Message, CallbackQuery))),
            kwargs.get("message") or kwargs.get("callback_query"),
        )
        state = next(
            (arg for arg in args if isinstance(arg, FSMContext)), kwargs.get("state")
        )

        if message_or_query is None or state is None:
            raise ValueError(
                "Handler must receive Message or CallbackQuery and FSMContext"
            )

        user_id = message_or_query.from_user.id
        user_language_code = await get_user_language(user_id, state.storage)

        return await handler(
            *args, lang_code=user_language_code, user_id=user_id, **kwargs
        )

    return wrapper
