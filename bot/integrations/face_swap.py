import asyncio

import aiohttp
import httpx
from filetype import filetype

from bot.config import config

FACE_SWAP_API_URL = "https://developer.remaker.ai/api/remaker"
FACE_SWAP_API_KEY = config.FACE_SWAP_API_KEY.get_secret_value()


class FaceSwap:
    def __init__(self, session: aiohttp.ClientSession = None) -> None:
        self.headers = {
            "accept": "application/json",
            "authorization": FACE_SWAP_API_KEY,
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
        async with self.session.request(
            method, url, headers=self.headers, **kwargs
        ) as response:
            response.raise_for_status()
            return await response.json()


class APIResource:
    def __init__(self, client: FaceSwap) -> None:
        self._client = client

    async def request(self, method: str, url: str, **kwargs):
        return await self._client.request(method, url, **kwargs)


class Videos(APIResource):
    async def generate(
        self,
        image_url: str,
        video_url: str,
    ) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response_content = response.content

        kind = await asyncio.to_thread(lambda: filetype.guess(response_content))
        if kind:
            media_type = kind.mime
            extension = kind.extension
        else:
            media_type = "image/jpeg"
            extension = "jpeg"

        form_data = aiohttp.FormData()
        form_data.add_field("target_video_url", video_url)
        form_data.add_field(
            "swap_image",
            response_content,
            filename=f"uploaded_image.{extension}",
            content_type=media_type,
        )

        data = await self.request(
            "POST",
            f"{FACE_SWAP_API_URL}/v2/face-swap-video/create-job",
            data=form_data,
        )
        return data["result"]["job_id"]

    async def get_generation(
        self,
        job_id: str,
    ):
        data = await self.request(
            "GET", f"{FACE_SWAP_API_URL}/v2/face-swap-video/{job_id}"
        )
        return data["result"]


async def generate_face_swap_video(
    image_url: str,
    video_url: str,
) -> str:
    async with FaceSwap() as client:
        task_id = await client.videos.generate(
            image_url=image_url,
            video_url=video_url,
        )

        return task_id


async def get_face_swap_video_generation(
    job_id: str,
) -> dict:
    async with FaceSwap() as client:
        generation = await client.videos.get_generation(
            job_id=job_id,
        )

        return generation
