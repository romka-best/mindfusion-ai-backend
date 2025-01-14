import aiohttp

from bot.config import config
from bot.database.models.common import SunoVersion

SUNO_API_URL = 'https://api.acedata.cloud/suno/audios'
SUNO_API_KEY = config.SUNO_API_KEY.get_secret_value()
WEBHOOK_SUNO_URL = config.WEBHOOK_URL + config.WEBHOOK_SUNO_PATH


class Suno:
    def __init__(self, session: aiohttp.ClientSession = None) -> None:
        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {SUNO_API_KEY}',
        }
        self.session = session

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

        self.songs = Songs(self)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def request(self, method: str, url: str, **kwargs):
        async with self.session.request(method, url, headers=self.headers, **kwargs) as response:
            response.raise_for_status()
            return await response.json()


class APIResource:
    def __init__(self, client: Suno) -> None:
        self._client = client

    async def request(self, method: str, url: str, **kwargs):
        return await self._client.request(method, url, **kwargs)


class Songs(APIResource):
    async def generate(
        self,
        version: SunoVersion,
        prompt: str,
        instrumental: bool = False,
        custom: bool = False,
        tags: str = ''
    ) -> str:
        payload = {
            'action': 'generate',
            'model': version,
            'lyric': prompt if custom else '',
            'prompt': '' if custom else prompt,
            'custom': custom,
            'instrumental': instrumental,
            'style': tags if custom else '',
            'callback_url': WEBHOOK_SUNO_URL,
        }
        data = await self.request('POST', SUNO_API_URL, json=payload)
        return data['task_id']


async def generate_song(
    version: SunoVersion,
    prompt: str,
    instrumental: bool = False,
    custom: bool = False,
    tags: str = ''
) -> str:
    async with Suno() as client:
        task_id = await client.songs.generate(
            version=version,
            prompt=prompt,
            instrumental=instrumental,
            custom=custom,
            tags=tags,
        )

        return task_id
