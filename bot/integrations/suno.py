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
            'authorization': f'bearer {SUNO_API_KEY}',
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
        self, version: SunoVersion, prompt: str, instrumental: bool = False, custom: bool = False, tags: str = ""
    ) -> str:
        payload = {
            "action": "generate",
            "model": version,
            "lyric": prompt if custom else "",
            "prompt": "" if custom else prompt,
            "custom": custom,
            "instrumental": instrumental,
            "style": tags if custom else "",
            "callback_url": WEBHOOK_SUNO_URL,
        }
        data = await self.request("POST", SUNO_API_URL, json=payload)
        return data["task_id"]

    async def extend(self, version: SunoVersion, style, audio_id, lyric, continue_at) -> str:
        payload = {
            "action": "extend",
            "model": version,
            "style": style,
            "audio_id": audio_id,
            "lyric": lyric,
            "continue_at": continue_at,
            "callback_url": WEBHOOK_SUNO_URL,
        }

        data = await self.request("POST", SUNO_API_URL, json=payload)
        return data["task_id"]

    async def concat(self, audio_id) -> str:
        payload = {
          "action": "concat",
          "audio_id": audio_id,
          "callback_url": WEBHOOK_SUNO_URL,
        }

        data = await self.request("POST", SUNO_API_URL, json=payload)
        return data["task_id"]

async def generate_song(*args, **kwargs) -> str:
    async with Suno() as client:
        return await client.songs.generate(*args, **kwargs)

async def extend_song(*args, **kwargs) -> str:
    async with Suno() as client:
        return await client.songs.extend(*args, **kwargs)

async def concat_song(*args, **kwargs) -> str:
    async with Suno() as client:
        return await client.songs.concat(*args, **kwargs)
