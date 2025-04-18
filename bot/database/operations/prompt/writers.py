from bot.database.main import firebase
from bot.database.models.common import ModelType
from bot.database.models.prompt import Prompt, PromptCategory, PromptSubCategory
from bot.database.operations.prompt.helpers import (
    create_prompt_category_object,
    create_prompt_object,
    create_prompt_subcategory_object,
)
from bot.locales.types import LanguageCode


async def write_prompt(
    product_ids: list[str],
    subcategory_ids: list[str],
    names: dict[LanguageCode, str],
    short_prompts: dict[LanguageCode, str],
    long_prompts: dict[LanguageCode, str],
    has_examples: bool = False,
) -> Prompt:
    prompt = await create_prompt_object(
        product_ids,
        subcategory_ids,
        names,
        short_prompts,
        long_prompts,
        has_examples,
    )
    await (
        firebase.db.collection(Prompt.COLLECTION_NAME)
        .document(prompt.id)
        .set(prompt.to_dict())
    )

    return prompt


async def write_prompt_category(
    model_type: ModelType,
    names: dict[LanguageCode, str],
) -> PromptCategory:
    prompt_category = await create_prompt_category_object(
        model_type,
        names,
    )
    await (
        firebase.db.collection(PromptCategory.COLLECTION_NAME)
        .document(prompt_category.id)
        .set(prompt_category.to_dict())
    )

    return prompt_category


async def write_prompt_subcategory(
    category_ids: list[str],
    names: dict[LanguageCode, str],
) -> PromptSubCategory:
    prompt_subcategory = await create_prompt_subcategory_object(
        category_ids,
        names,
    )
    await (
        firebase.db.collection(PromptSubCategory.COLLECTION_NAME)
        .document(prompt_subcategory.id)
        .set(prompt_subcategory.to_dict())
    )

    return prompt_subcategory
