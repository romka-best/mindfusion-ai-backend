from typing_extensions import Optional

from aiogram.client.session import aiohttp

from bot.config import config
from bot.database.models.common import (
    AspectRatio,
    KlingDuration,
    KlingMode,
    KlingVersion,
)

KLING_API_URL = "https://api.piapi.ai"
KLING_API_KEY = config.KLING_API_KEY.get_secret_value()
WEBHOOK_KLING_URL = config.WEBHOOK_URL + config.WEBHOOK_KLING_PATH


class Kling:
    def __init__(self, session: aiohttp.ClientSession = None) -> None:
        self.headers = {"Content-Type": "application/json", "x-api-key": KLING_API_KEY}
        self.session = session

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

        self.videos = Videos(self)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def request(self, method: str, url: str, **kwargs):
        async with self.session.request(
            method, url, headers=self.headers, **kwargs
        ) as response:
            response.raise_for_status()
            return await response.json()

    @staticmethod
    def get_cost_for_video(mode: KlingMode, duration: KlingDuration):
        if mode == KlingMode.PRO and duration == KlingDuration.SECONDS_10:
            return 3
        elif mode == KlingMode.PRO or duration == KlingDuration.SECONDS_10:
            return 2

        return 1

    @staticmethod
    def get_price_for_video(mode: KlingMode, duration: KlingDuration):
        if mode == KlingMode.PRO and duration == KlingDuration.SECONDS_10:
            return 0.92
        elif mode == KlingMode.PRO and duration == KlingDuration.SECONDS_5:
            return 0.46
        elif mode == KlingMode.STANDARD and duration == KlingDuration.SECONDS_10:
            return 0.26
        elif mode == KlingMode.STANDARD and duration == KlingDuration.SECONDS_5:
            return 0.13

        return 0


class APIResource:
    def __init__(self, client: Kling) -> None:
        self._client = client

    async def request(self, method: str, url: str, **kwargs):
        return await self._client.request(method, url, **kwargs)


class Videos(APIResource):
    async def generate(
        self,
        prompt: str,
        version: KlingVersion,
        mode: KlingMode,
        duration: KlingDuration,
        aspect_ratio: AspectRatio,
        image_url: Optional[str] = None,
    ) -> str:
        url = f"{KLING_API_URL}/api/v1/task"
        payload = {
            "model": "kling",
            "task_type": "video_generation",
            "input": {
                "prompt": prompt,
                "version": version,
                "mode": mode,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "image_url": image_url,
                "cfg_scale": 0.5,
            },
            "config": {
                "webhook_config": {
                    "endpoint": WEBHOOK_KLING_URL,
                }
            },
        }
        data = await self.request("POST", url, json=payload)
        return data["data"]["task_id"]


async def generate_video(
    prompt: str,
    version: KlingVersion,
    mode: KlingMode,
    duration: KlingDuration,
    aspect_ratio: AspectRatio,
    image_url: Optional[str] = None,
) -> str:
    async with Kling() as client:
        video_id = await client.videos.generate(
            prompt=prompt,
            version=version,
            mode=mode,
            duration=duration,
            aspect_ratio=aspect_ratio,
            image_url=image_url,
        )

        return video_id
