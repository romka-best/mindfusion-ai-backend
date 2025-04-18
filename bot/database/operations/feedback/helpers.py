from bot.database.main import firebase
from bot.database.models.feedback import Feedback


async def create_feedback_object(user_id: str, content: str) -> Feedback:
    feedback_ref = firebase.db.collection(Feedback.COLLECTION_NAME).document()

    return Feedback(id=feedback_ref.id, user_id=user_id, content=content)
