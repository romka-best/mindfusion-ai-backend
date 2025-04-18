from anthropic import AsyncAnthropic

from bot.config import config
from bot.database.models.common import ClaudeGPTVersion

client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY.get_secret_value())


def get_default_max_tokens(model_version: ClaudeGPTVersion) -> int:
    base = 1024
    if (
        model_version == ClaudeGPTVersion.V3_Haiku
        or model_version == ClaudeGPTVersion.V3_Sonnet
        or model_version == ClaudeGPTVersion.V3_Opus
    ):
        return base

    return base


async def get_response_message(
    model_version: ClaudeGPTVersion, system_prompt: str, history: list
) -> dict:
    max_tokens = get_default_max_tokens(model_version)

    response = await client.messages.create(
        model=model_version,
        system=system_prompt,
        messages=history,
        max_tokens=max_tokens,
    )

    return {
        "finish_reason": response.stop_reason,
        "message": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
