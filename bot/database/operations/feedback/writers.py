from bot.database.main import firebase
from bot.database.models.feedback import Feedback
from bot.database.operations.feedback.helpers import create_feedback_object


async def write_feedback(user_id: str, content: str) -> Feedback:
    feedback = await create_feedback_object(user_id, content)
    await (
        firebase.db.collection(Feedback.COLLECTION_NAME)
        .document(feedback.id)
        .set(feedback.to_dict())
    )

    return feedback
