from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.promo_code import PromoCode


async def update_promo_code(promo_code_id: str, data: dict):
    promo_code_id_ref = firebase.db.collection(PromoCode.COLLECTION_NAME).document(
        promo_code_id
    )
    data["edited_at"] = datetime.now(timezone.utc)

    await promo_code_id_ref.update(data)
