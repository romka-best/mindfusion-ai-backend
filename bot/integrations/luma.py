from typing import Optional

from lumaai import AsyncLumaAI, NOT_GIVEN

from bot.config import config
from bot.database.models.common import AspectRatio, LumaPhotonVersion

WEBHOOK_LUMA_URL = config.WEBHOOK_URL + config.WEBHOOK_LUMA_PATH

client = AsyncLumaAI(
    auth_token=config.LUMA_API_KEY.get_secret_value(),
)


async def get_response_image(
    prompt_text: str,
    aspect_ratio: AspectRatio,
    prompt_image: Optional[str] = None,
) -> str:
    response = await client.generations.image.create(
        model=LumaPhotonVersion.V1,
        prompt=prompt_text,
        aspect_ratio=aspect_ratio,
        callback_url=WEBHOOK_LUMA_URL,
        modify_image_ref=NOT_GIVEN if not prompt_image else {
            'url': prompt_image,
            'weight': 0.5,
        },
    )

    return response.id


async def get_response_video(
    prompt_text: str,
    aspect_ratio: AspectRatio,
    prompt_image: Optional[str] = None,
) -> str:
    response = await client.generations.video.create(
        prompt=prompt_text,
        aspect_ratio=aspect_ratio,
        callback_url=WEBHOOK_LUMA_URL,
        keyframes=NOT_GIVEN if not prompt_image else {
            'frame0': {
                'type': 'image',
                'url': prompt_image,
            }
        }
    )

    return response.id
