import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand, BotCommandScopeChat

from bot.config import config
from bot.locales.types import LanguageCode

commands_en = [
    BotCommand(
        command='start',
        description='👋 About bot',
    ),
    BotCommand(
        command='model',
        description='🤖 Select AI Model',
    ),
    BotCommand(
        command='profile',
        description='👤 Profile',
    ),
    BotCommand(
        command='buy',
        description='💎 Subscriptions and Packages',
    ),
    BotCommand(
        command='text',
        description='🔤 Generate Text',
    ),
    BotCommand(
        command='summary',
        description='📝 Generate Summary',
    ),
    BotCommand(
        command='image',
        description='🖼 Generate Images',
    ),
    BotCommand(
        command='music',
        description='🎵 Generate Music',
    ),
    BotCommand(
        command='video',
        description='📹 Generate Videos',
    ),
    BotCommand(
        command='info',
        description='ℹ️ About AI models',
    ),
    BotCommand(
        command='catalog',
        description='📂 Prompts and Roles',
    ),
    BotCommand(
        command='settings',
        description='🔧 Customize AI model',
    ),
    BotCommand(
        command='language',
        description='🌍 Select Language',
    ),
    BotCommand(
        command='help',
        description='🛟 Help and Commands',
    ),
]

commands_ru = [
    BotCommand(
        command='start',
        description='👋 Что умеет бот',
    ),
    BotCommand(
        command='model',
        description='🤖 Выбрать AI модель',
    ),
    BotCommand(
        command='profile',
        description='👤 Профиль',
    ),
    BotCommand(
        command='buy',
        description='💎 Подписки и пакеты',
    ),
    BotCommand(
        command='text',
        description='🔤 Генерация текста',
    ),
    BotCommand(
        command='summary',
        description='📝 Генерация резюме',
    ),
    BotCommand(
        command='image',
        description='🖼 Генерация изображений',
    ),
    BotCommand(
        command='music',
        description='🎵 Генерация музыки',
    ),
    BotCommand(
        command='video',
        description='📹 Генерация видео',
    ),
    BotCommand(
        command='info',
        description='ℹ️ Про нейросети',
    ),
    BotCommand(
        command='catalog',
        description='📂 Промпты и роли',
    ),
    BotCommand(
        command='settings',
        description='🔧 Настройки нейросети',
    ),
    BotCommand(
        command='language',
        description='🌍 Поменять язык',
    ),
    BotCommand(
        command='help',
        description='🛟 Помощь и команды',
    ),
]

commands_es = [
    BotCommand(
        command='start',
        description='👋 Qué puede hacer el bot',
    ),
    BotCommand(
        command='model',
        description='🤖 Elegir modelo de IA',
    ),
    BotCommand(
        command='profile',
        description='👤 Perfil',
    ),
    BotCommand(
        command='buy',
        description='💎 Suscripciones y paquetes',
    ),
    BotCommand(
        command='text',
        description='🔤 Generación de texto',
    ),
    BotCommand(
        command='summary',
        description='📝 Generación de resúmenes',
    ),
    BotCommand(
        command='image',
        description='🖼 Generación de imágenes',
    ),
    BotCommand(
        command='music',
        description='🎵 Generación de música',
    ),
    BotCommand(
        command='video',
        description='📹 Generación de video',
    ),
    BotCommand(
        command='info',
        description='ℹ️ Sobre las redes neuronales',
    ),
    BotCommand(
        command='catalog',
        description='📂 Prompts y roles',
    ),
    BotCommand(
        command='settings',
        description='🔧 Configuración de IA',
    ),
    BotCommand(
        command='language',
        description='🌍 Cambiar idioma',
    ),
    BotCommand(
        command='help',
        description='🛟 Ayuda y comandos',
    ),
]

commands_hi = [
    BotCommand(
        command='start',
        description='👋 बॉट क्या कर सकता है',
    ),
    BotCommand(
        command='model',
        description='🤖 AI मॉडल चुनें',
    ),
    BotCommand(
        command='profile',
        description='👤 प्रोफ़ाइल',
    ),
    BotCommand(
        command='buy',
        description='💎 सब्सक्रिप्शन और पैकेज',
    ),
    BotCommand(
        command='text',
        description='🔤 टेक्स्ट जनरेशन',
    ),
    BotCommand(
        command='summary',
        description='📝 सारांश जनरेशन',
    ),
    BotCommand(
        command='image',
        description='🖼 इमेज जनरेशन',
    ),
    BotCommand(
        command='music',
        description='🎵 म्यूजिक जनरेशन',
    ),
    BotCommand(
        command='video',
        description='📹 वीडियो जनरेशन',
    ),
    BotCommand(
        command='info',
        description='ℹ️ न्यूरल नेटवर्क के बारे में',
    ),
    BotCommand(
        command='catalog',
        description='📂 प्रॉम्प्ट्स और भूमिकाएं',
    ),
    BotCommand(
        command='settings',
        description='🔧 AI सेटिंग्स',
    ),
    BotCommand(
        command='language',
        description='🌍 भाषा बदलें',
    ),
    BotCommand(
        command='help',
        description='🛟 मदद और कमांड्स',
    ),
]

commands_admin = commands_ru + [
    BotCommand(command='admin', description='👨‍💻 Админка'),
]


async def set_commands(bot: Bot):
    await bot.set_my_commands(commands=commands_en)
    await bot.set_my_commands(commands=commands_ru, language_code=LanguageCode.RU)
    await bot.set_my_commands(commands=commands_es, language_code=LanguageCode.ES)
    await bot.set_my_commands(commands=commands_hi, language_code=LanguageCode.HI)

    for chat_id in config.ADMIN_IDS:
        try:
            await bot.set_my_commands(commands=commands_admin, scope=BotCommandScopeChat(chat_id=chat_id))
        except TelegramBadRequest as error:
            if error.message.startswith('Bad Request: chat not found'):
                logging.warning(f'{error.message}: {chat_id}')
            else:
                raise error


async def set_commands_for_user(bot: Bot, chat_id: str, language=LanguageCode):
    try:
        if language == LanguageCode.RU:
            await bot.set_my_commands(commands=commands_ru, scope=BotCommandScopeChat(chat_id=chat_id))
        elif language == LanguageCode.ES:
            await bot.set_my_commands(commands=commands_es, scope=BotCommandScopeChat(chat_id=chat_id))
        elif language == LanguageCode.HI:
            await bot.set_my_commands(commands=commands_hi, scope=BotCommandScopeChat(chat_id=chat_id))
        else:
            await bot.set_my_commands(commands=commands_en, scope=BotCommandScopeChat(chat_id=chat_id))
    except TelegramBadRequest as error:
        if error.message.startswith('Bad Request: chat not found'):
            logging.warning(f'{error.message}: {chat_id}')
        else:
            raise error
