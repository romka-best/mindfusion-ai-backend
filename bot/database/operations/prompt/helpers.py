from bot.database.main import firebase
from bot.database.models.common import ModelType
from bot.database.models.prompt import Prompt, PromptCategory, PromptSubCategory
from bot.locales.types import LanguageCode


async def create_prompt_object(
    product_ids: list[str],
    subcategory_ids: list[str],
    names: dict[LanguageCode, str],
    short_prompts: dict[LanguageCode, str],
    long_prompts: dict[LanguageCode, str],
    has_examples: bool = False,
) -> Prompt:
    prompt_ref = firebase.db.collection(Prompt.COLLECTION_NAME).document()
    return Prompt(
        id=prompt_ref.id,
        product_ids=product_ids,
        subcategory_ids=subcategory_ids,
        names=names,
        short_prompts=short_prompts,
        long_prompts=long_prompts,
        has_examples=has_examples,
    )


async def create_prompt_category_object(
    model_type: ModelType,
    names: dict[LanguageCode, str],
) -> PromptCategory:
    prompt_category_ref = firebase.db.collection(
        PromptCategory.COLLECTION_NAME
    ).document()
    return PromptCategory(
        id=prompt_category_ref.id,
        type=model_type,
        names=names,
    )


async def create_prompt_subcategory_object(
    category_ids: list[str],
    names: dict[LanguageCode, str],
) -> PromptSubCategory:
    prompt_subcategory_ref = firebase.db.collection(
        PromptSubCategory.COLLECTION_NAME
    ).document()
    return PromptSubCategory(
        id=prompt_subcategory_ref.id,
        category_ids=category_ids,
        names=names,
    )
