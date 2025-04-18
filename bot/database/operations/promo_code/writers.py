from bot.database.main import firebase
from bot.database.models.promo_code import PromoCode, PromoCodeType, UsedPromoCode
from bot.database.operations.promo_code.helpers import (
    create_promo_code_object,
    create_used_promo_code_object,
)


async def write_promo_code(
    created_by_user_id: str,
    name: str,
    type: PromoCodeType,
    details: dict,
    until=None,
) -> PromoCode:
    promo_code = await create_promo_code_object(
        created_by_user_id, name, type, details, until
    )
    await (
        firebase.db.collection(PromoCode.COLLECTION_NAME)
        .document(promo_code.id)
        .set(promo_code.to_dict())
    )

    return promo_code


async def write_used_promo_code(user_id: str, promo_code_id: str) -> UsedPromoCode:
    used_promo_code = await create_used_promo_code_object(user_id, promo_code_id)
    await (
        firebase.db.collection(UsedPromoCode.COLLECTION_NAME)
        .document(used_promo_code.id)
        .set(used_promo_code.to_dict())
    )

    return used_promo_code
