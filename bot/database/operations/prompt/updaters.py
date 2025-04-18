from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.prompt import Prompt, PromptCategory, PromptSubCategory


async def update_prompt(prompt_id: str, data: dict):
    prompt_ref = firebase.db.collection(Prompt.COLLECTION_NAME).document(prompt_id)
    data["edited_at"] = datetime.now(timezone.utc)

    await prompt_ref.update(data)


async def update_prompt_category(prompt_category_id: str, data: dict):
    prompt_category_ref = firebase.db.collection(
        PromptCategory.COLLECTION_NAME
    ).document(prompt_category_id)
    data["edited_at"] = datetime.now(timezone.utc)

    await prompt_category_ref.update(data)


async def update_prompt_subcategory(prompt_subcategory_id: str, data: dict):
    prompt_subcategory_ref = firebase.db.collection(
        PromptSubCategory.COLLECTION_NAME
    ).document(prompt_subcategory_id)
    data["edited_at"] = datetime.now(timezone.utc)

    await prompt_subcategory_ref.update(data)
