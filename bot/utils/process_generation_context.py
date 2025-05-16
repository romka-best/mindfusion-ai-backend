from contextlib import AsyncContextDecorator

from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.operations.generation.getters import get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request


class ProcessGenerationContext(AsyncContextDecorator):
    def __init__(self, message: Message, sticker, text, user_id, product_id, request_details=None):
        self.message = message
        self.sticker = sticker
        self.text = text
        self.processing_sticker = None
        self.processing_message = None
        self.user_id = user_id
        self.product_id = product_id
        self.generation = []
        self.request = None
        self.request_details = request_details

    async def __aenter__(self):
        # Send process ui msgs
        self.processing_sticker = await self.message.answer_sticker(
            sticker=config.MESSAGE_STICKERS.get(self.sticker),
        )
        self.processing_message = await self.message.reply(
            text=self.text,
            allow_sending_without_reply=True,
        )

        # Fire header bot action bar
        self.chat_action = ChatActionSender.upload_video(
            bot=self.message.bot,
            chat_id=self.message.chat.id,
        )

        # Create STARTED request record
        self.request = await write_request(
            user_id=self.user_id,
            processing_message_ids=[self.processing_sticker.message_id, self.processing_message.message_id],
            product_id=self.product_id,
            requested=1,
            details=self.request_details,
        )

        await self.chat_action.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.chat_action.__aexit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            await self.processing_sticker.delete()
            await self.processing_message.delete()

            if self.request:
                self.request.status = RequestStatus.FINISHED
                await update_request(self.request.id, {"status": self.request.status})

            if self.generation:
                generations = await get_generations_by_request_id(self.request.id)
                for generation in generations:
                    generation.status = GenerationStatus.FINISHED
                    generation.has_error = True
                    await update_generation(
                        generation.id,
                        {
                            "status": generation.status,
                            "has_error": generation.has_error,
                        },
                    )

        return False  # Suppress exception
