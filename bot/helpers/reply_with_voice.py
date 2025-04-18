import asyncio
from typing import Literal, Optional

from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, Message

from bot.database.models.common import Currency, Quota
from bot.database.models.transaction import TransactionType
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.transaction.writers import write_transaction
from bot.integrations.open_ai import get_response_text_to_speech


async def reply_with_voice(
    message: Message,
    text: str,
    user_id: str,
    reply_markup: Optional[InlineKeyboardMarkup],
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
):
    audio_content = await get_response_text_to_speech(text, voice)

    product = await get_product_by_quota(Quota.VOICE_MESSAGES)

    total_price = 0.000015 * len(text)
    await write_transaction(
        user_id=user_id,
        type=TransactionType.EXPENSE,
        product_id=product.id,
        amount=total_price,
        clear_amount=total_price,
        currency=Currency.USD,
        quantity=1,
        details={
            "subtype": "TTS",
            "text": text,
            "has_error": False,
        },
    )

    file = await asyncio.to_thread(audio_content.read)
    await message.reply_voice(
        voice=BufferedInputFile(file, filename="answer.ogg"),
        reply_markup=reply_markup,
        allow_sending_without_reply=True,
    )
