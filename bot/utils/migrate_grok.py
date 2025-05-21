import re

from aiogram import Bot

from bot.database.main import firebase
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers

GROK_OLD = "grok_2"
GROK_NEW = "grok_3"


def replace_grok_2(text):
    return re.sub(r"Grok 2", "Grok 3", text)

def replace_grok_3(text):
    return re.sub(r"Grok 3", "Grok 2", text)

async def migrate_users():
    async for user_doc in firebase.db.collection("users").stream():
        user_data = user_doc.to_dict()
        updates = {}

        # Migrate daily_limits
        daily_limits = user_data.get("daily_limits", {})
        if GROK_OLD in daily_limits:
            value = daily_limits[GROK_OLD]
            daily_limits[GROK_NEW] = value
            del daily_limits[GROK_OLD]
            updates["daily_limits"] = daily_limits

        # Migrate additional_usage_quota
        additional_quota = user_data.get("additional_usage_quota", {})
        if GROK_OLD in additional_quota:
            value = additional_quota[GROK_OLD]
            additional_quota[GROK_NEW] = value
            del additional_quota[GROK_OLD]
            updates["additional_usage_quota"] = additional_quota

        settings = user_data.get("settings", {})
        settings.get("grok", {})["version"] = "grok-3"

        updates["settings"] = settings

        if updates:
            print(f"ADD users settings daily, additional_quota {user_doc.id}")
            await firebase.db.collection("users").document(user_doc.id).update(updates)


async def migrate_products():
    async for product_doc in firebase.db.collection("products").stream():
        product = product_doc.to_dict()
        updates = {}

        # Если это подписка
        if product.get("type") == "SUBSCRIPTION":
            limits = product.get("details", {}).get("limits", {})
            if GROK_OLD in limits:
                limits[GROK_NEW] = limits[GROK_OLD]
                del limits[GROK_OLD]
                product.get("details", {})["limits"] = limits
                updates["details"] = product.get("details", {})

        # Если это пакет
        if product.get("type") == "PACKAGE":
            # Обновляем details.quota
            details = product.get("details", {})
            if details.get("quota") == GROK_OLD:
                details["quota"] = GROK_NEW

                details["support_documents"] = False
                details["support_photos"] = False

                updates["details"] = details

            # Обновляем names
            names = product.get("names", {})
            updated_names = {lang: replace_grok_2(name) for lang, name in names.items() if "Grok 2" in name}
            if updated_names:
                names.update(updated_names)
                updates["names"] = names

            # Обновляем descriptions
            descriptions = product.get("descriptions", {})
            updated_descs = {lang: replace_grok_2(desc) for lang, desc in descriptions.items() if "Grok 2" in desc}
            if updated_descs:
                descriptions.update(updated_descs)
                updates["descriptions"] = descriptions

        if updates:
            print(f"UPDATE product grok_2 -> grok_3 {product_doc.id}")
            await firebase.db.collection("products").document(product_doc.id).update(updates)

async def down():
    async for user_doc in firebase.db.collection("users").stream():
        user_data = user_doc.to_dict()
        updates = {}

        # Migrate daily_limits
        daily_limits = user_data.get("daily_limits", {})
        if GROK_NEW in daily_limits:
            value = daily_limits[GROK_NEW]
            daily_limits[GROK_OLD] = value
            del daily_limits[GROK_NEW]
            updates["daily_limits"] = daily_limits

        # Migrate additional_usage_quota
        additional_quota = user_data.get("additional_usage_quota", {})
        if GROK_NEW in additional_quota:
            value = additional_quota[GROK_NEW]
            additional_quota[GROK_OLD] = value
            del additional_quota[GROK_NEW]
            updates["additional_usage_quota"] = additional_quota

        settings = user_data.get("settings", {})
        settings.get("grok", {})["version"] = "grok-2"

        updates["settings"] = settings

        if updates:
            print(f"DELETE users settings daily, additional_quota {user_doc.id}")
            await firebase.db.collection("users").document(user_doc.id).update(updates)



    async for product_doc in firebase.db.collection("products").stream():
        product = product_doc.to_dict()
        updates = {}

        # Если это подписка
        if product.get("type") == "SUBSCRIPTION":
            limits = product.get("details", {}).get("limits", {})
            if GROK_NEW in limits:
                limits[GROK_OLD] = limits[GROK_NEW]
                del limits[GROK_NEW]
                product.get("details", {})["limits"] = limits
                updates["details"] = product.get("details", {})

        # Если это пакет
        if product.get("type") == "PACKAGE":
            # Обновляем details.quota
            details = product.get("details", {})
            if details.get("quota") == GROK_NEW:
                details["quota"] = GROK_OLD

                details["support_documents"] = False
                details["support_photos"] = False

                updates["details"] = details

            # Обновляем names
            names = product.get("names", {})
            updated_names = {lang: replace_grok_3(name) for lang, name in names.items() if "Grok 3" in name}
            if updated_names:
                names.update(updated_names)
                updates["names"] = names

            # Обновляем descriptions
            descriptions = product.get("descriptions", {})
            updated_descs = {lang: replace_grok_3(desc) for lang, desc in descriptions.items() if "Grok 3" in desc}
            if updated_descs:
                descriptions.update(updated_descs)
                updates["descriptions"] = descriptions

        if updates:
            print(f"DELETE grok_3 -> grok_2 product {product_doc.id}")
            await firebase.db.collection("products").document(product_doc.id).update(updates)


async def up():
    await migrate_users()
    await migrate_products()

async def migrate(bot: Bot):
    await down()
    await up()

    await send_message_to_admins_and_developers(bot, "<b>Database Migration Was Successful!</b> 🎉")
