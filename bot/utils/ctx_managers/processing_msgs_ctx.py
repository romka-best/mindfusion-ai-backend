import asyncio
from contextlib import AsyncContextDecorator


class ProcessingMsgsCtx(AsyncContextDecorator):
    def __init__(self, msg, sticker, text):
        self.msg = msg
        self.sticker = sticker
        self.text = text
        self.sticker_msg = None
        self.text_msg = None
        self.ids = [] # processing messages ids

    async def __aenter__(self):
        self.sticker_msg = await self.msg.answer_sticker(sticker=self.sticker)
        self.text_msg = await self.msg.answer(text=self.text)
        self.ids.extend([self.sticker_msg.message_id, self.text_msg.message_id])

        return self

    async def __aexit__(self, exc_type, *args):
        if exc_type is not None:
            await self.sticker_msg.delete()
            await self.text_msg.delete()

