from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter, Query

from bot.database.main import firebase
from bot.database.models.face_swap_package import (
    FaceSwapPackage,
    FaceSwapPackageStatus,
    UsedFaceSwapPackage,
)
from bot.database.models.user import UserGender


async def get_face_swap_package(face_swap_package_id: str) -> Optional[FaceSwapPackage]:
    face_swap_package_ref = firebase.db.collection(
        FaceSwapPackage.COLLECTION_NAME
    ).document(str(face_swap_package_id))
    face_swap_package = await face_swap_package_ref.get()

    if face_swap_package.exists:
        return FaceSwapPackage(**face_swap_package.to_dict())


async def get_face_swap_package_by_name_and_gender(
    name: str,
    gender: UserGender,
) -> Optional[FaceSwapPackage]:
    face_swap_package_stream = (
        firebase.db.collection(FaceSwapPackage.COLLECTION_NAME)
        .where(filter=FieldFilter("name", "==", name))
        .where(filter=FieldFilter("gender", "==", gender))
        .limit(1)
        .stream()
    )

    async for doc in face_swap_package_stream:
        return FaceSwapPackage(**doc.to_dict())


async def get_face_swap_packages(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[FaceSwapPackage]:
    face_swap_packages_query = firebase.db.collection(FaceSwapPackage.COLLECTION_NAME)

    if start_date:
        face_swap_packages_query = face_swap_packages_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        face_swap_packages_query = face_swap_packages_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    face_swap_packages = face_swap_packages_query.order_by(
        "created_at", direction=Query.ASCENDING
    ).stream()
    return [
        FaceSwapPackage(**face_swap_package.to_dict())
        async for face_swap_package in face_swap_packages
    ]


async def get_face_swap_packages_by_gender(
    gender: UserGender,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[FaceSwapPackageStatus] = None,
) -> list[FaceSwapPackage]:
    face_swap_packages_query = firebase.db.collection(
        FaceSwapPackage.COLLECTION_NAME
    ).where(filter=FieldFilter("gender", "==", gender))

    if start_date:
        face_swap_packages_query = face_swap_packages_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        face_swap_packages_query = face_swap_packages_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )
    if status:
        face_swap_packages_query = face_swap_packages_query.where(
            filter=FieldFilter("status", "==", status)
        )

    face_swap_packages = face_swap_packages_query.order_by(
        "created_at", direction=Query.ASCENDING
    ).stream()
    return [
        FaceSwapPackage(**face_swap_package.to_dict())
        async for face_swap_package in face_swap_packages
    ]


async def get_used_face_swap_package(
    used_face_swap_package_id: str,
) -> Optional[UsedFaceSwapPackage]:
    used_face_swap_package_ref = firebase.db.collection(
        UsedFaceSwapPackage.COLLECTION_NAME
    ).document(str(used_face_swap_package_id))
    used_face_swap_package = await used_face_swap_package_ref.get()

    if used_face_swap_package.exists:
        return UsedFaceSwapPackage(**used_face_swap_package.to_dict())


async def get_used_face_swap_package_by_user_id_and_package_id(
    user_id: str,
    package_id: str,
) -> Optional[UsedFaceSwapPackage]:
    used_face_swap_package_stream = (
        firebase.db.collection(UsedFaceSwapPackage.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .where(filter=FieldFilter("package_id", "==", package_id))
        .limit(1)
        .stream()
    )

    async for doc in used_face_swap_package_stream:
        return UsedFaceSwapPackage(**doc.to_dict())


async def get_used_face_swap_packages_by_user_id(
    user_id: str,
) -> list[UsedFaceSwapPackage]:
    used_face_swap_packages_stream = (
        firebase.db.collection(UsedFaceSwapPackage.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .order_by("created_at", direction=Query.DESCENDING)
        .stream()
    )
    used_face_swap_packages = [
        UsedFaceSwapPackage(**used_face_swap_package.to_dict())
        async for used_face_swap_package in used_face_swap_packages_stream
    ]

    return used_face_swap_packages


async def get_used_face_swap_packages(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[UsedFaceSwapPackage]:
    used_face_swap_packages_query = firebase.db.collection(
        UsedFaceSwapPackage.COLLECTION_NAME
    )

    if start_date:
        used_face_swap_packages_query = used_face_swap_packages_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        used_face_swap_packages_query = used_face_swap_packages_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    used_face_swap_packages = used_face_swap_packages_query.stream()
    return [
        UsedFaceSwapPackage(**used_face_swap_package.to_dict())
        async for used_face_swap_package in used_face_swap_packages
    ]
