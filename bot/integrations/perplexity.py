import openai

from bot.config import config
from bot.database.models.common import PerplexityGPTVersion

client = openai.AsyncOpenAI(
    api_key=config.PERPLEXITY_API_KEY.get_secret_value(),
    base_url="https://api.perplexity.ai",
)


async def get_response_message(
    model_version: PerplexityGPTVersion,
    history: list,
) -> dict:
    response = await client.chat.completions.create(
        model=model_version,
        messages=history,
    )

    return {
        "finish_reason": response.choices[0].finish_reason,
        "message": response.choices[0].message,
        "citations": response.citations if hasattr(response, "citations") else [],
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
    }
