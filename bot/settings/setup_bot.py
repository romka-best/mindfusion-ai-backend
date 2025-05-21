# python -m bot.settings.setup_bot
# Helps fill settings/config_* files

import asyncio
import logging

from aiogram import Bot, Dispatcher , types
from aiogram.filters import Command


from bot.config import config
logging.basicConfig(level=logging.INFO)


bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()


@dp.message()
async def handle_all_messages(message: types.Message):
    user_id = message.from_user.id

    if user_id != "616315442": # TODO Поменяй меня
        return

    await message.reply(f"user id {user_id}")

    if message.effect_id:
        await message.reply(f"effect id {message.effect_id}")
    if message.sticker:
        await message.reply(f"sticker id {message.sticker.file_id}")
    if message.photo:
        await message.reply(f"photo id {message.photo[-1].file_id}")

async def main():
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

