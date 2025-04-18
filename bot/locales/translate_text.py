import json
import logging

from aiogram.client.session import aiohttp

from bot.config import config


async def get_translate_token() -> str:
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    headers = {"Content-Type": "application/json"}
    data = {"yandexPassportOauthToken": config.OAUTH_YANDEX_TOKEN.get_secret_value()}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                token_data = await response.json()
                return token_data.get("iamToken", "")
            else:
                error_message = await response.text()
                logging.exception(f"Error trying to get IAM_TOKEN: {error_message}")
                return ""


async def translate_text(
    text: str, source_language_code: str, target_language_code: str
):
    token = await get_translate_token()
    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "folder_id": "b1gauqcr90jd0sdpald9",
        "sourceLanguageCode": source_language_code,
        "targetLanguageCode": target_language_code,
        "texts": [text],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, headers=headers, data=json.dumps(payload)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["translations"][0]["text"]
            else:
                error_message = await response.text()
                logging.exception(f"Error in translate_text: {error_message}")
                return ""
