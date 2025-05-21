import io
import os
import asyncio
from aiogram import Bot
from google.cloud import firestore
from google.cloud.firestore_v1.field_path import FieldPath
from bot.database.main import firebase
from bot.database.models.user import User
from aiogram.types import BufferedInputFile


MIGRATE_CHAT_ID = "-4752921470"

MAX_RETRIES = 10
RETRY_DELAY = 2

# FIELD
async def user_field_lora_up():
    users_ref = firebase.db.collection("users")
    bulk_writer = firebase.db.bulk_writer()

    async for user in users_ref.stream():
        doc_ref = users_ref.document(user.id)
        bulk_writer.update(doc_ref, {"face_swap_lora_version": ""})
        print(f"ADD face_swap_lora_version {user.id}")

    bulk_writer.flush()

async def user_field_lora_down():
    users_ref = firebase.db.collection("users")
    bulk_writer = firebase.db.bulk_writer()

    async for user in users_ref.stream():
        doc_ref = users_ref.document(user.id)
        bulk_writer.update(doc_ref, {"face_swap_lora_version": firestore.DELETE_FIELD})
        print(f"DELETE face_swap_lora_version {user.id}")

    bulk_writer.flush()

# PHOTOS
async def send_photo_with_retry(bot, chat_id, buffer, filename):
    file_data = buffer.read()
    input_file = BufferedInputFile(file_data, filename=filename)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return await bot.send_photo(chat_id=chat_id, photo=input_file)
        except Exception as e:
            print(f"Попытка {filename} {attempt} не удалась: {e}")
            if attempt == MAX_RETRIES:
                return None
            await asyncio.sleep(RETRY_DELAY)


async def migrate_user_avatars(bot: Bot):
    # Get all files and dirs in /users/avatars/
    bucket = firebase.bucket
    blobs = (await bucket.list_blobs(prefix="users/avatars/"))[1:]

    file_paths = set()

    for blob_name in blobs:
        parts = blob_name.split('/')
        if len(parts) == 3:
            file_paths.add(blob_name)
        elif len(parts) == 4:
            file_paths.add(f"{parts[0]}/{parts[1]}/{parts[2]}/")
    # /

    # Get all users
    users = firebase.db.collection(User.COLLECTION_NAME).stream()
    user_ids = set()

    async for doc in users:
        user_data = doc.to_dict()
        user_ids.add(user_data["id"])

    total_to_migarte = len(user_ids)
    current_migrated = 0
    # /


    # Iterate and move existed photos
    for file_path in file_paths:
        print(f"Status: {total_to_migarte}/{current_migrated}")

        if file_path.count('/') > 2:
            user_id = file_path.split("/")[2]
            user_ids.remove(user_id)

            print(f"Папка для {user_id} уже есть")
            current_migrated += 1
            continue

        filename = os.path.basename(file_path)
        possible_user_id = os.path.splitext(filename)[0]

        if possible_user_id not in user_ids:
            print(f"Пропущен (не найден user_id): {filename}")
            continue

        data = await bucket.storage.download(bucket.name, file_path)
        buffer = io.BytesIO(data)

        message = await send_photo_with_retry(bot, MIGRATE_CHAT_ID, buffer, filename)

        if message is None:
            print(f"Ошибка миграции {file_path}")
            continue

        file_id = message.photo[-1].file_id
        print(f"Отправили фото в тг {file_path} получили {file_id}")


        ext = os.path.splitext(filename)[1]
        new_filename = f"0_{file_id}{ext}"
        new_path = f"users/avatars/{possible_user_id}/{new_filename}"


        buffer.seek(0)
        await firebase.bucket.new_blob(new_path).upload(buffer)
        print(f"загружаем в {new_path} и удаляем старый")


        await firebase.storage.delete(bucket=firebase.bucket.name, object_name=file_path)

        print(f"Перемещено: {file_path} → {new_path}")
        current_migrated += 1
        user_ids.remove(possible_user_id)

    # Create dirs for rest users with no photos
    for user_id in user_ids:
        print(f"Status: {total_to_migarte}/{current_migrated}")
        fake_dir_blob_name = f"users/avatars/{user_id}/"
        empty_blob = firebase.bucket.new_blob(fake_dir_blob_name)

        await empty_blob.upload(b"")

        print(f"Создана директория для {user_id}")
        current_migrated += 1


async def up():
    await user_field_lora_up()

async def down():
    await user_field_lora_down()

async def migrate(bot):
    #await down()
    await up()

    await migrate_user_avatars(bot)
    print("END OF PHOTO MIGRATION")
    print("-----------------------")

