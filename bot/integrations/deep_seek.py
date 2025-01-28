import openai

from bot.config import config
from bot.database.models.common import DeepSeekVersion

client = openai.AsyncOpenAI(
    api_key=config.DEEPSEEK_API_KEY.get_secret_value(),
    base_url='https://api.deepseek.com',
)


async def get_response_message(
    model_version: DeepSeekVersion,
    history: list,
) -> dict:
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
