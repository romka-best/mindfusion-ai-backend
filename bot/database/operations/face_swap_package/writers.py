from bot.database.main import firebase
from bot.database.models.face_swap_package import (
    FaceSwapFileData,
    FaceSwapPackage,
    FaceSwapPackageStatus,
    UsedFaceSwapPackage,
)
from bot.database.models.user import UserGender
from bot.database.operations.face_swap_package.helpers import (
    create_face_swap_package_object,
    create_used_face_swap_package_object,
)


async def write_face_swap_package(
    name: str,
    translated_names: dict,
    gender: UserGender,
    files: list[FaceSwapFileData],
    status: FaceSwapPackageStatus,
) -> FaceSwapPackage:
    face_swap_package = await create_face_swap_package_object(
        name, translated_names, gender, files, status
    )
    await (
        firebase.db.collection(FaceSwapPackage.COLLECTION_NAME)
        .document(face_swap_package.id)
        .set(face_swap_package.to_dict())
    )

    return face_swap_package


async def write_used_face_swap_package(
    user_id: str,
    package_id: str,
    used_images: list[str],
) -> UsedFaceSwapPackage:
    used_face_swap_package = await create_used_face_swap_package_object(
        user_id, package_id, used_images
    )
    await (
        firebase.db.collection(UsedFaceSwapPackage.COLLECTION_NAME)
        .document(used_face_swap_package.id)
        .set(used_face_swap_package.to_dict())
    )

    return used_face_swap_package
