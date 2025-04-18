from bot.database.main import firebase
from bot.database.models.face_swap_package import (
    FaceSwapFileData,
    FaceSwapPackage,
    FaceSwapPackageStatus,
    UsedFaceSwapPackage,
)
from bot.database.models.user import UserGender


async def create_face_swap_package_object(
    name: str,
    translated_names: dict,
    gender: UserGender,
    files: list[FaceSwapFileData],
    status: FaceSwapPackageStatus,
) -> FaceSwapPackage:
    face_swap_package_ref = firebase.db.collection(
        FaceSwapPackage.COLLECTION_NAME
    ).document()
    return FaceSwapPackage(
        id=face_swap_package_ref.id,
        name=name,
        translated_names=translated_names,
        gender=gender,
        files=files,
        status=status,
    )


async def create_used_face_swap_package_object(
    user_id: str,
    package_id: str,
    used_images: list[str],
) -> UsedFaceSwapPackage:
    used_face_swap_package_ref = firebase.db.collection(
        UsedFaceSwapPackage.COLLECTION_NAME
    ).document()
    return UsedFaceSwapPackage(
        id=used_face_swap_package_ref.id,
        user_id=user_id,
        package_id=package_id,
        used_images=used_images,
    )
