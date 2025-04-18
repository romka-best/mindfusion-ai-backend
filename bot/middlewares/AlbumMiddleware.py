import asyncio
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 2.0):
        self.latency = latency
        self.albums = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: dict[str, Any],
    ):
        if message.media_group_id:
            if message.media_group_id not in self.albums:
                self.albums[message.media_group_id] = []
                asyncio.create_task(
                    self.dispatch_album(message.media_group_id, handler, data, message)
                )
            self.albums[message.media_group_id].append(message)
        else:
            data["album"] = []
            await handler(message, data)

    async def dispatch_album(
        self,
        media_group_id: str,
        handler: Callable,
        data: dict[str, Any],
        message: Message,
    ):
        await asyncio.sleep(self.latency)
        album = self.albums.pop(media_group_id, [])
        if album:
            data["album"] = album
            await handler(message, data)
