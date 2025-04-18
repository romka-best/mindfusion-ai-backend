from bot.database.main import firebase
from bot.database.models.campaign import Campaign
from bot.database.operations.campaign.helpers import create_campaign_object


async def write_campaign(
    utm: dict,
    discount=0,
) -> Campaign:
    campaign = await create_campaign_object(
        utm,
        discount,
    )
    await (
        firebase.db.collection(Campaign.COLLECTION_NAME)
        .document(campaign.id)
        .set(campaign.to_dict())
    )

    return campaign
