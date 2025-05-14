from typing import BinaryIO, Literal

import openai

from bot.config import config
from bot.database.models.common import ChatGPTVersion, DALLEResolution, DALLEQuality, DALLEVersion

client = openai.AsyncOpenAI(
    api_key=config.OPENAI_API_KEY.get_secret_value(),
)


def get_default_max_tokens(model_version: ChatGPTVersion) -> int:
    base = 1024
    if (
        model_version == ChatGPTVersion.V4_Omni_Mini or
        model_version == ChatGPTVersion.V4_Omni
    ):
        return base

    return base


async def get_response_message(model_version: ChatGPTVersion, history: list) -> dict:
    max_tokens = get_default_max_tokens(model_version)

    if model_version == ChatGPTVersion.V4_Omni_Mini or model_version == ChatGPTVersion.V4_Omni:
        response = await client.chat.completions.create(
            model=model_version,
            messages=history,
            max_tokens=max_tokens,
        )
    else:
        response = await client.chat.completions.create(
            model=model_version,
            messages=history,
        )

    return {
        'finish_reason': response.choices[0].finish_reason,
        'message': response.choices[0].message,
        'input_tokens': response.usage.prompt_tokens,
        'output_tokens': response.usage.completion_tokens,
    }


def get_cost_for_image(quality: DALLEQuality, resolution: DALLEResolution):
    if quality == DALLEQuality.STANDARD and resolution == DALLEResolution.LOW:
        return 1
    elif quality == DALLEQuality.STANDARD and (
        resolution == DALLEResolution.MEDIUM or resolution == DALLEResolution.HIGH
    ):
        return 2
    elif quality == DALLEQuality.HD and resolution == DALLEResolution.LOW:
        return 2
    elif quality == DALLEQuality.HD and (resolution == DALLEResolution.MEDIUM or resolution == DALLEResolution.HIGH):
        return 3
    return 1


async def get_response_image(
    version,
    prompt,
    size=None,
    quality=None,
    background=None,
    moderation="low",
    output_compression=None,
    output_format=None,
    response_format=None,
    style=None,
    user=None,
    n=1,
) -> str:
    args = {
        "model": version,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "background": background,
        "moderation": moderation,
        "output_compression": output_compression,
        "output_format": output_format,
        "response_format": response_format,
        "style": style,
        "user": user,
        "n": n,
    }

    args = {k: v for k, v in args.items() if v is not None}

    return await client.images.generate(**args)


async def get_response_speech_to_text(audio_file: BinaryIO) -> str:
    response = await client.audio.transcriptions.create(
        model='whisper-1',
        file=audio_file,
    )

    return response.text


async def get_response_text_to_speech(text: str, voice: Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']):
    response = await client.audio.speech.create(
        model='tts-1',
        voice=voice,
        response_format='opus',
        input=text,
    )

    return response
