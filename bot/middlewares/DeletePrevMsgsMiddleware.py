import re
from aiogram import BaseMiddleware
from typing import Callable, Any
from aiogram.types import CallbackQuery, TelegramObject


class DeletePrevMsgsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: dict[str, Any],
    ):
        callback_query: CallbackQuery = getattr(event, "callback_query", None)
        if callback_query and callback_query.data:
            pattern = re.compile(r"^(\d+)\|(.+)")

            if callback_query.data:
                match = pattern.match(callback_query.data)
                if match:
                    number_part, info_part = match.groups()

                    try:
                        data["delete_prev_msgs_num"] = int(number_part)
                    except ValueError:
                        data["delete_prev_msgs_num"] = 0

                    event.callback_query.__dict__["data"] = info_part # Hack because event object is frozen
                else:
                    data["delete_prev_msg_nums"] = 0

        return await handler(event, data)
