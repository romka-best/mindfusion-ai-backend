from typing import Optional

from google.cloud.firestore_v1 import FieldFilter

from bot.database.main import firebase
from bot.database.models.campaign import Campaign


async def get_campaign(campaign_id: str) -> Optional[Campaign]:
    campaign_ref = firebase.db.collection(Campaign.COLLECTION_NAME).document(
        str(campaign_id)
    )
    campaign = await campaign_ref.get()

    if campaign.exists:
        return Campaign(**campaign.to_dict())


async def get_campaign_by_name(name: str) -> Optional[Campaign]:
    campaign_stream = (
        firebase.db.collection(Campaign.COLLECTION_NAME)
        .where(filter=FieldFilter("utm.campaign", "==", name))
        .limit(1)
        .stream()
    )

    async for doc in campaign_stream:
        return Campaign(**doc.to_dict())
