import aiohttp

from bot.config import config
from bot.database.models.common import VideoSummaryFocus, VideoSummaryFormat, VideoSummaryAmount
from bot.locales.types import LanguageCode

EIGHTIFY_API_URL = 'https://backend.eightify.app'
EIGHTIFY_API_KEY = config.EIGHTIFY_API_KEY.get_secret_value()


class Eightify:
    def __init__(self, session: aiohttp.ClientSession = None) -> None:
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {EIGHTIFY_API_KEY}'
        }
        self.session = session

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

        self.summary = Summary(self)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def request(self, method: str, url: str, **kwargs):
        async with self.session.request(method, url, headers=self.headers, **kwargs) as response:
            response.raise_for_status()
            return await response.json()


class APIResource:
    def __init__(self, client: Eightify) -> None:
        self._client = client

    async def request(self, method: str, url: str, **kwargs):
        return await self._client.request(method, url, **kwargs)


class Summary(APIResource):
    async def generate(
        self,
        language_code: LanguageCode,
        video_id: str,
        focus: VideoSummaryFocus,
        format: VideoSummaryFormat,
        amount: VideoSummaryAmount,
    ) -> str:
        url = f'{EIGHTIFY_API_URL}/api/summarization/flexible-insights'
        payload = {
            'is_auto_summary': False,
            'language': language_code.upper(),
            'settings': {
                'focus': focus,
                'format': format,
                'amount': amount,
                'modifiers': [
                    'group',
                ],
            },
            'source': 'side-block-button',
            'video_id': video_id,
        }
        data = await self.request('POST', url, json=payload)
        return data['markdown']


async def generate_summary(
    language_code: LanguageCode,
    video_id: str,
    focus: VideoSummaryFocus,
    format: VideoSummaryFormat,
    amount: VideoSummaryAmount,
) -> str:
    async with Eightify() as client:
        summary = await client.summary.generate(
            language_code=language_code,
            video_id=video_id,
            focus=focus,
            format=format,
            amount=amount,
        )

        return summary
