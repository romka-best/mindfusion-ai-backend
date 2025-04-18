from typing import Optional

from google.cloud.firestore_v1 import FieldFilter, Query

from bot.database.main import firebase
from bot.database.models.common import ModelType
from bot.database.models.prompt import Prompt, PromptCategory, PromptSubCategory


async def get_prompt(prompt_id: str) -> Optional[Prompt]:
    prompt_ref = firebase.db.collection(Prompt.COLLECTION_NAME).document(str(prompt_id))
    prompt = await prompt_ref.get()

    if prompt.exists:
        return Prompt(**prompt.to_dict())


async def get_prompt_category(prompt_category_id: str) -> Optional[PromptCategory]:
    prompt_category_ref = firebase.db.collection(
        PromptCategory.COLLECTION_NAME
    ).document(str(prompt_category_id))
    prompt_category = await prompt_category_ref.get()

    if prompt_category.exists:
        return PromptCategory(**prompt_category.to_dict())


async def get_prompt_subcategory(
    prompt_subcategory_id: str,
) -> Optional[PromptSubCategory]:
    prompt_subcategory_ref = firebase.db.collection(
        PromptSubCategory.COLLECTION_NAME
    ).document(str(prompt_subcategory_id))
    prompt_subcategory = await prompt_subcategory_ref.get()

    if prompt_subcategory.exists:
        return PromptSubCategory(**prompt_subcategory.to_dict())


async def get_prompt_categories_by_model_type(
    model_type: ModelType,
) -> list[PromptCategory]:
    prompt_categories = (
        firebase.db.collection(PromptCategory.COLLECTION_NAME)
        .where(filter=FieldFilter("type", "==", model_type))
        .order_by("created_at", direction=Query.DESCENDING)
        .stream()
    )

    return [
        PromptCategory(**prompt_category.to_dict())
        async for prompt_category in prompt_categories
    ]


async def get_prompt_subcategories_by_category_id(
    category_id: str,
) -> list[PromptSubCategory]:
    prompt_categories = (
        firebase.db.collection(PromptSubCategory.COLLECTION_NAME)
        .where(filter=FieldFilter("category_ids", "array_contains", category_id))
        .order_by("created_at", direction=Query.DESCENDING)
        .stream()
    )

    return [
        PromptSubCategory(**prompt_category.to_dict())
        async for prompt_category in prompt_categories
    ]


async def get_prompts_by_subcategory_id(
    subcategory_id: str,
) -> list[Prompt]:
    prompts = (
        firebase.db.collection(Prompt.COLLECTION_NAME)
        .where(filter=FieldFilter("subcategory_ids", "array_contains", subcategory_id))
        .order_by("created_at", direction=Query.DESCENDING)
        .stream()
    )

    return [Prompt(**prompt.to_dict()) async for prompt in prompts]


async def get_prompts_by_product_id_and_subcategory_id(
    product_id: str,
    subcategory_id: str,
) -> list[Prompt]:
    prompts = (
        firebase.db.collection(Prompt.COLLECTION_NAME)
        .where(filter=FieldFilter("product_ids", "array_contains", product_id))
        .where(filter=FieldFilter("subcategory_ids", "array_contains", subcategory_id))
        .order_by("created_at", direction=Query.DESCENDING)
        .stream()
    )

    return [Prompt(**prompt.to_dict()) async for prompt in prompts]
