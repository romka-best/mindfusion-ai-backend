from bot.database.main import firebase
from bot.database.models.promo_code import PromoCode, PromoCodeType, UsedPromoCode


async def create_promo_code_object(
    created_by_user_id: str,
    name: str,
    type: PromoCodeType,
    details: dict,
    until=None,
) -> PromoCode:
    promo_code_ref = firebase.db.collection(PromoCode.COLLECTION_NAME).document()

    return PromoCode(
        id=promo_code_ref.id,
        created_by_user_id=created_by_user_id,
        name=name,
        type=type,
        details=details,
        until=until,
    )


async def create_used_promo_code_object(
    user_id: str,
    promo_code_id: str,
) -> UsedPromoCode:
    used_promo_code_ref = firebase.db.collection(
        UsedPromoCode.COLLECTION_NAME
    ).document()

    return UsedPromoCode(
        id=used_promo_code_ref.id, user_id=user_id, promo_code_id=promo_code_id
    )
