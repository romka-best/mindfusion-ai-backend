from bot.database.main import firebase
from bot.database.models.campaign import Campaign


async def create_campaign_object(
    utm: dict,
    discount=0,
) -> Campaign:
    campaign_ref = firebase.db.collection(Campaign.COLLECTION_NAME).document()
    return Campaign(
        id=campaign_ref.id,
        utm=utm,
        discount=discount,
    )
