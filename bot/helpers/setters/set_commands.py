import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand, BotCommandScopeChat

from bot.config import config
from bot.locales.types import LanguageCode

commands_en = [
    BotCommand(
        command='start',
        description='👋 About this bot',
    ),
    BotCommand(
        command='model',
        description='🤖 Select AI model',
    ),
    BotCommand(
        command='profile',
        description='👤 Profile',
    ),
    BotCommand(
        command='buy',
        description='💎 Buy a subscription or packages',
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
        description='ℹ️ Info about AI models',
    ),
    BotCommand(
        command='catalog',
        description='📂 Catalog with prompts and digital employees',
    ),
    BotCommand(
        command='settings',
        description='🔧 Customize AI model',
    ),
    BotCommand(
        command='language',
        description='🌍 Select language',
    ),
    BotCommand(
        command='help',
        description='🛟 Help and Commands',
    ),
]

commands_ru = [
    BotCommand(
        command='start',
        description='👋 Что умеет этот бот',
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
        description='👋 Qué puede hacer este bot',
    ),
    BotCommand(
        command='model',
        description='🤖 Seleccionar modelo IA',
    ),
    BotCommand(
        command='profile',
        description='👤 Perfil',
    ),
    BotCommand(
        command='buy',
        description='💎 Comprar suscripción o paquetes',
    ),
    BotCommand(
        command='text',
        description='🔤 Generación de texto con: ChatGPT, Claude, Gemini, Grok, Perplexity',
    ),
    BotCommand(
        command='summary',
        description='📝 Generación de resúmenes en: YouTube, Video',
    ),
    BotCommand(
        command='image',
        description='🖼 Generación de imágenes con: DALL-E, Midjourney, Stable Diffusion, Flux, Luma Photon, FaceSwap, Photoshop IA',
    ),
    BotCommand(
        command='music',
        description='🎵 Generación de música con: MusicGen, Suno',
    ),
    BotCommand(
        command='video',
        description='📹 Generación de video con: Kling, Runway, Luma Ray',
    ),
    BotCommand(
        command='info',
        description='ℹ️ Información sobre modelos AI',
    ),
    BotCommand(
        command='catalog',
        description='📂 Catálogo de prompts y empleados digitales',
    ),
    BotCommand(
        command='settings',
        description='🔧 Configurar el modelo a tu medida',
    ),
    BotCommand(
        command='language',
        description='🌍 Cambiar idioma',
    ),
    BotCommand(
        command='help',
        description='🛟 Información detallada sobre comandos',
    ),
]

commands_hi = [
    BotCommand(
        command='start',
        description='👋 इस बॉट की क्षमताएँ जानें',
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
        description='💎 सदस्यता या पैकेज खरीदें',
    ),
    BotCommand(
        command='text',
        description='🔤 टेक्स्ट जनरेशन: ChatGPT, Claude, Gemini, Grok, Perplexity से',
    ),
    BotCommand(
        command='summary',
        description='📝 सारांश जनरेशन: YouTube, वीडियो से',
    ),
    BotCommand(
        command='image',
        description='🖼 छवियों का निर्माण: DALL-E, Midjourney, Stable Diffusion, Flux, Luma Photon, FaceSwap, Photoshop AI से',
    ),
    BotCommand(
        command='music',
        description='🎵 संगीत निर्माण: MusicGen, Suno से',
    ),
    BotCommand(
        command='video',
        description='📹 वीडियो निर्माण: Kling, Runway, Luma Ray से',
    ),
    BotCommand(
        command='info',
        description='ℹ️ AI मॉडल की जानकारी',
    ),
    BotCommand(
        command='catalog',
        description='📂 प्रॉम्प्ट और डिजिटल सहायक की सूची',
    ),
    BotCommand(
        command='settings',
        description='🔧 अपनी जरूरतों के अनुसार मॉडल सेट करें',
    ),
    BotCommand(
        command='language',
        description='🌍 भाषा बदलें',
    ),
    BotCommand(
        command='help',
        description='🛟 कमांड की विस्तृत जानकारी',
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
