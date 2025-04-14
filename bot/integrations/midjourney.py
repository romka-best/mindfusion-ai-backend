from aiogram.client.session import aiohttp

from bot.config import config
from bot.database.models.common import MidjourneyVersion, MidjourneyAction, AspectRatio

MIDJOURNEY_API_URL = 'https://api.piapi.ai'
MIDJOURNEY_API_KEY = config.MIDJOURNEY_API_KEY.get_secret_value()
WEBHOOK_MIDJOURNEY_URL = config.WEBHOOK_URL + config.WEBHOOK_MIDJOURNEY_PATH


class Midjourney:
    def __init__(self, session: aiohttp.ClientSession = None) -> None:
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': MIDJOURNEY_API_KEY,
        }
        self.session = session

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

        self.images = Images(self)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def request(self, method: str, url: str, **kwargs):
        async with self.session.request(method, url, headers=self.headers, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    @staticmethod
    def get_price_for_image(version: MidjourneyVersion, action: MidjourneyAction):
        if action == MidjourneyAction.UPSCALE:
            return 0.01
        elif version == MidjourneyVersion.V5 and action in [
            MidjourneyAction.IMAGINE,
            MidjourneyAction.REROLL,
            MidjourneyAction.VARIATION,
        ]:
            return 0.015
        elif version == MidjourneyVersion.V6 and action in [
            MidjourneyAction.IMAGINE,
            MidjourneyAction.REROLL,
            MidjourneyAction.VARIATION,
        ]:
            return 0.07
        elif version == MidjourneyVersion.V7 and action in [
            MidjourneyAction.IMAGINE,
            MidjourneyAction.REROLL,
            MidjourneyAction.VARIATION,
        ]:
            return 0.12

        return 0

    @staticmethod
    def get_cost_for_image(version: MidjourneyVersion):
        if version == MidjourneyVersion.V7:
            return 2

        return 1


class APIResource:
    def __init__(self, client: Midjourney) -> None:
        self._client = client

    async def request(self, method: str, url: str, **kwargs):
        return await self._client.request(method, url, **kwargs)


class Images(APIResource):
    async def imagine(
        self,
        prompt: str,
        process_mode: str,
        aspect_ratio: AspectRatio = None
    ) -> str:
        url = f'{MIDJOURNEY_API_URL}/api/v1/task'
        payload = {
            'model': 'midjourney',
            'task_type': 'imagine',
            'input': {
                'prompt': prompt,
                'process_mode': process_mode,
            },
            'config': {
                'webhook_config': {
                    'endpoint': WEBHOOK_MIDJOURNEY_URL,
                }
            },
        }

        if aspect_ratio:
            payload['input']['aspect_ratio'] = aspect_ratio

        data = await self.request('POST', url, json=payload)
        return data['data']['task_id']

    async def upscale(
        self,
        task_id: str,
        choice: int,
    ) -> str:
        url = f'{MIDJOURNEY_API_URL}/api/v1/task'
        payload = {
            'model': 'midjourney',
            'task_type': 'upscale',
            'input': {
                'origin_task_id': task_id,
                'index': str(choice),
            },
            'config': {
                'webhook_config': {
                    'endpoint': WEBHOOK_MIDJOURNEY_URL,
                }
            },
        }
        data = await self.request('POST', url, json=payload)
        return data['data']['task_id']

    async def reroll(
        self,
        task_id: str,
    ) -> str:
        url = f'{MIDJOURNEY_API_URL}/api/v1/task'
        payload = {
            'model': 'midjourney',
            'task_type': 'reroll',
            'input': {
                'origin_task_id': task_id,
            },
            'config': {
                'webhook_config': {
                    'endpoint': WEBHOOK_MIDJOURNEY_URL,
                }
            },
        }
        data = await self.request('POST', url, json=payload)
        return data['data']['task_id']

    async def variation(
        self,
        task_id: str,
        choice: int,
    ) -> str:
        url = f'{MIDJOURNEY_API_URL}/api/v1/task'
        payload = {
            'model': 'midjourney',
            'task_type': 'variation',
            'input': {
                'origin_task_id': task_id,
                'index': str(choice),
            },
            'config': {
                'webhook_config': {
                    'endpoint': WEBHOOK_MIDJOURNEY_URL,
                }
            },
        }
        data = await self.request('POST', url, json=payload)
        return data['data']['task_id']


async def create_midjourney_images(
    prompt: str,
    process_mode: str,
    aspect_ratio: AspectRatio = None,
) -> str:
    async with Midjourney() as client:
        task_id = await client.images.imagine(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            process_mode=process_mode,
        )

        return task_id


async def create_midjourney_image(
    original_task_id: str,
    choice: int,
) -> str:
    async with Midjourney() as client:
        task_id = await client.images.upscale(
            task_id=original_task_id,
            choice=choice,
        )

        return task_id


async def create_different_midjourney_images(
    original_task_id: str,
) -> str:
    async with Midjourney() as client:
        task_id = await client.images.reroll(
            task_id=original_task_id,
        )

        return task_id


async def create_different_midjourney_image(
    original_task_id: str,
    choice: int,
) -> str:
    async with Midjourney() as client:
        task_id = await client.images.variation(
            task_id=original_task_id,
            choice=choice,
        )

        return task_id
