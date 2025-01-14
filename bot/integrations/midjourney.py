import logging
from typing import Optional

from aiogram.client.session import aiohttp

from bot.config import config

MIDJOURNEY_API_URL = 'https://api.userapi.ai'
MIDJOURNEY_API_KEY = config.MIDJOURNEY_API_KEY.get_secret_value()
WEBHOOK_MIDJOURNEY_URL = config.WEBHOOK_URL + config.WEBHOOK_MIDJOURNEY_PATH


async def create_midjourney_images(prompt: str):
    url = MIDJOURNEY_API_URL + '/midjourney/v2/imagine'
    headers = {
        'api-key': MIDJOURNEY_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'prompt': prompt,
        'webhook_url': WEBHOOK_MIDJOURNEY_URL,
        'webhook_type': 'result',
        'is_disable_prefilter': False,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('hash', '')
            else:
                error_message = await response.text()
                logging.exception(f'Error in create_midjourney_images: {error_message}')
                return ''


async def create_midjourney_image(hash_id: str, choice: int) -> Optional[str]:
    url = MIDJOURNEY_API_URL + '/midjourney/v2/upscale'
    headers = {
        'api-key': MIDJOURNEY_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'hash': hash_id,
        'choice': choice,
        'webhook_url': WEBHOOK_MIDJOURNEY_URL,
        'webhook_type': 'result',
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('hash', '')
            else:
                error_message = await response.text()
                logging.exception(f'Error in create_midjourney_image: {error_message}')
                return ''


async def create_different_midjourney_images(hash_id: str) -> Optional[str]:
    url = MIDJOURNEY_API_URL + '/midjourney/v2/reroll'
    headers = {
        'api-key': MIDJOURNEY_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'hash': hash_id,
        'webhook_url': WEBHOOK_MIDJOURNEY_URL,
        'webhook_type': 'result',
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('hash', '')
            else:
                error_message = await response.text()
                logging.exception(f'Error in create_different_midjourney_images: {error_message}')
                return ''


async def create_different_midjourney_image(hash_id: str, choice: int) -> Optional[str]:
    url = MIDJOURNEY_API_URL + '/midjourney/v2/variation'
    headers = {
        'api-key': MIDJOURNEY_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'hash': hash_id,
        'choice': choice,
        'webhook_url': WEBHOOK_MIDJOURNEY_URL,
        'webhook_type': 'result',
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('hash', '')
            else:
                error_message = await response.text()
                logging.exception(f'Error in create_different_midjourney_image: {error_message}')
                return ''
