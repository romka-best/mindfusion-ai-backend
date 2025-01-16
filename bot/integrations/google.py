import asyncio
import io

import httpx
from filetype import filetype
from google.generativeai import configure, GenerativeModel, GenerationConfig, upload_file, get_file
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from bot.config import config
from bot.database.models.common import GeminiGPTVersion

configure(api_key=config.GEMINI_API_KEY.get_secret_value())


def get_default_max_tokens(model_version: GeminiGPTVersion) -> int:
    base = 1024
    if (
        model_version == GeminiGPTVersion.V2_Flash or
        model_version == GeminiGPTVersion.V1_Pro
    ):
        return base
    elif model_version == GeminiGPTVersion.V1_Ultra:
        return base * 2

    return base


async def get_response_message(
    model_version: GeminiGPTVersion,
    system_prompt: str,
    history: list,
) -> dict:
    max_tokens = get_default_max_tokens(model_version)

    if model_version == GeminiGPTVersion.V1_Ultra:
        model_name = GeminiGPTVersion.V1_Pro
    else:
        model_name = model_version
    model = GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
    )
    response = await model.generate_content_async(
        contents=history,
        generation_config=GenerationConfig(
            max_output_tokens=max_tokens,
        ),
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    return {
        'finish_reason': response.candidates[-1].finish_reason,
        'message': response.text,
        'input_tokens': response.usage_metadata.prompt_token_count,
        'output_tokens': response.usage_metadata.candidates_token_count,
    }


async def get_response_video_summary(
    prompt: str,
    video_file_link: str,
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.head(video_file_link)
        mime_type = response.headers.get('Content-Type')
        if not mime_type.startswith('video/'):
            raise ValueError(f'Unsupported MIME type: {mime_type}')

        response = await client.get(video_file_link)
        video_content = response.content
    video_io = io.BytesIO(video_content)
    video_file = await asyncio.to_thread(lambda: upload_file(path=video_io, mime_type=mime_type))

    while video_file.state.name == 'PROCESSING':
        await asyncio.sleep(10)
        video_file = await asyncio.to_thread(lambda: get_file(video_file.name))

    if video_file.state.name == 'FAILED':
        raise ValueError(video_file.state.name)

    model_name = GeminiGPTVersion.V2_Flash
    model = GenerativeModel(
        model_name=model_name,
    )
    response = await model.generate_content_async(
        contents=[video_file, prompt],
        request_options={'timeout': 600},
    )

    return {
        'finish_reason': response.candidates[-1].finish_reason,
        'message': response.text,
        'input_tokens': response.usage_metadata.prompt_token_count,
        'output_tokens': response.usage_metadata.candidates_token_count,
    }
