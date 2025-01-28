import aiohttp

from bot.config import config
from bot.database.models.common import PikaVersion

PIKA_API_URL = 'https://api.acedata.cloud/pika/videos'
PIKA_API_KEY = config.PIKA_API_KEY.get_secret_value()
WEBHOOK_PIKA_URL = config.WEBHOOK_URL + config.WEBHOOK_PIKA_PATH


class Pika:
    def __init__(self, session: aiohttp.ClientSession = None) -> None:
        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {PIKA_API_KEY}',
        }
        self.session = session

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

        self.videos = Videos(self)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def request(self, method: str, url: str, **kwargs):
        async with self.session.request(method, url, headers=self.headers, **kwargs) as response:
            response.raise_for_status()
            return await response.json()


class APIResource:
    def __init__(self, client: Pika) -> None:
        self._client = client

    async def request(self, method: str, url: str, **kwargs):
        return await self._client.request(method, url, **kwargs)


class Videos(APIResource):
    async def generate(
        self,
        prompt: str,
        version: PikaVersion,
        aspect_ratio: str,
        image_url: str = '',
    ) -> str:
        aspect_ratio = aspect_ratio.split(':')
        aspect_ratio = int(aspect_ratio[0]) / int(aspect_ratio[1])
        payload = {
            'action': 'generate',
            'prompt': prompt,
            'model': version,
            'aspect_ratio': aspect_ratio if not image_url else '',
            'image_url': [image_url] if image_url else [],
            'callback_url': WEBHOOK_PIKA_URL,
        }
        data = await self.request('POST', PIKA_API_URL, json=payload)
        return data['task_id']


async def generate_video(
    prompt: str,
    version: PikaVersion,
    aspect_ratio: str,
    image_url: str = '',
) -> str:
    async with Pika() as client:
        task_id = await client.videos.generate(
            prompt=prompt,
            version=version,
            aspect_ratio=aspect_ratio,
            image_url=image_url,
        )

        return task_id
