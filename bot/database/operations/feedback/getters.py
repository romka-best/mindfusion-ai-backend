from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter

from bot.database.main import firebase
from bot.database.models.feedback import Feedback, FeedbackStatus


async def get_feedback(feedback_id: str) -> Optional[Feedback]:
    feedback_ref = firebase.db.collection(Feedback.COLLECTION_NAME).document(
        feedback_id
    )
    feedback = await feedback_ref.get()

    if feedback.exists:
        return Feedback(**feedback.to_dict())


async def get_count_of_approved_feedbacks_by_user_id(user_id: str) -> int:
    feedbacks_query = (
        await firebase.db.collection(Feedback.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .where(filter=FieldFilter("status", "==", FeedbackStatus.APPROVED))
        .count()
        .get()
    )

    return int(feedbacks_query[0][0].value)


async def get_count_of_feedbacks(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[FeedbackStatus] = None,
) -> int:
    feedbacks_query = firebase.db.collection(Feedback.COLLECTION_NAME)

    if status:
        feedbacks_query = feedbacks_query.where(
            filter=FieldFilter("status", "==", status)
        )
    if start_date:
        feedbacks_query = feedbacks_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        feedbacks_query = feedbacks_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    feedbacks_aggregate_query = await feedbacks_query.count().get()

    return int(feedbacks_aggregate_query[0][0].value)


async def get_feedbacks(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Feedback]:
    feedbacks_query = firebase.db.collection(Feedback.COLLECTION_NAME)

    if start_date:
        feedbacks_query = feedbacks_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        feedbacks_query = feedbacks_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    feedbacks = feedbacks_query.stream()

    return [Feedback(**feedback.to_dict()) async for feedback in feedbacks]
