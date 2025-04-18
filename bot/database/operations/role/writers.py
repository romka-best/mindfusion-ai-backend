from bot.database.main import firebase
from bot.database.models.role import Role
from bot.database.operations.role.helpers import create_role_object
from bot.locales.types import LanguageCode


async def write_role(
    translated_names: dict[LanguageCode, str],
    translated_descriptions: dict[LanguageCode, str],
    translated_instructions: dict[LanguageCode, str],
    photo: str,
) -> Role:
    role = await create_role_object(
        translated_names, translated_descriptions, translated_instructions, photo
    )
    await (
        firebase.db.collection(Role.COLLECTION_NAME)
        .document(role.id)
        .set(role.to_dict())
    )

    return role
