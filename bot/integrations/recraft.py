import openai

from bot.config import config
from bot.database.models.common import RecraftVersion, AspectRatio

client = openai.AsyncOpenAI(
    api_key=config.RECRAFT_API_KEY.get_secret_value(),
    base_url='https://external.api.recraft.ai/v1',
)


def get_size_by_aspect_ratio(aspect_ratio: AspectRatio):
    if aspect_ratio == AspectRatio.SQUARE:
        return '1024x1024'
    elif aspect_ratio == AspectRatio.LANDSCAPE:
        return '1820x1024'
    elif aspect_ratio == AspectRatio.PORTRAIT:
        return '1024x1820'
    elif aspect_ratio == AspectRatio.STANDARD_HORIZONTAL:
        return '1536x1024'
    elif aspect_ratio == AspectRatio.STANDARD_VERTICAL:
        return '1024x1536'
    elif aspect_ratio == AspectRatio.BANNER_HORIZONTAL:
        return '1280x1024'
    elif aspect_ratio == AspectRatio.BANNER_VERTICAL:
        return '1024x1280'
    elif aspect_ratio == AspectRatio.CLASSIC_HORIZONTAL:
        return '1365x1024'
    elif aspect_ratio == AspectRatio.CLASSIC_VERTICAL:
        return '1024x1365'
    return '1024x1024'


async def get_response_image(
    prompt: str,
    model_version: RecraftVersion,
    aspect_ratio: AspectRatio,
) -> str:
    response = await client.images.generate(
        model=model_version,
        prompt=prompt,
        size=get_size_by_aspect_ratio(aspect_ratio),
        style='any',
        n=1,
    )

    return response.data[0].url


async def get_response_replace_background_image(
    prompt: str,
    image: str,
) -> str:
    response = await client.post(
        path='/images/replaceBackground',
        cast_to=dict,
        options={'headers': {'Content-Type': 'multipart/form-data'}},
        files={
            'image': image,
        },
        body={
            'prompt': prompt,
        },
    )

    return response['data'][0]['url']


async def get_response_vectorize_image(
    image: str,
) -> str:
    response = await client.post(
        path='/images/vectorize',
        cast_to=dict,
        options={'headers': {'Content-Type': 'multipart/form-data'}},
        files={
            'image': image,
        },
    )

    return response['data'][0]['url']
