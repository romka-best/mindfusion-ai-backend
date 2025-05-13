from aiogram import Bot

from bot.database.main import firebase
from bot.database.models.common import Model, Quota
from bot.database.models.product import ProductCategory, ProductType
from bot.database.operations.product.writers import write_product
from bot.helpers import gpt_image
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers
from bot.locales.texts import Texts


async def up(product_data, user_settings_gpt_image, limits):
    # Create product
    product = await write_product(**product_data)

    # Users
    async for user_doc in firebase.db.collection("users").stream():
        user_data = user_doc.to_dict()
        updates = {}

        daily_limits = user_data.get("daily_limits", {})
        daily_limits.update(limits)
        updates["daily_limits"] = daily_limits

        additional_quota = user_data.get("additional_usage_quota", {})
        additional_quota.update(limits)
        updates["additional_usage_quota"] = additional_quota

        settings = user_data.get("settings", {})
        settings.update(user_settings_gpt_image)
        updates["settings"] = settings

        if updates:
            await firebase.db.collection("users").document(user_doc.id).update(updates)


async def down():
    # Delete product
    query = firebase.db.collection("products").where("details.quota", "==", Quota.GPT_IMAGE)
    async for doc in query.stream():
        await doc.reference.delete()

    # Delete user settigns
    async for user_doc in firebase.db.collection("users").stream():
        user_data = user_doc.to_dict()
        updates = {}

        daily_limits = user_data.get("daily_limits", {})
        if Quota.GPT_IMAGE in daily_limits:
            del daily_limits["gpt_image"]
            updates["daily_limits"] = daily_limits

        additional_quota = user_data.get("additional_usage_quota", {})
        if Quota.GPT_IMAGE in additional_quota:
            del additional_quota["gpt_image"]
            updates["additional_usage_quota"] = additional_quota

        settings = user_data.get("settings", {})
        if Model.GPT_IMAGE in settings:
            del settings["gpt-image"]
            updates["settings"] = settings

        if updates:
            await firebase.db.collection("users").document(user_doc.id).update(updates)


async def migrate(bot: Bot):
    # TODO change values
    product_data = {
        "stripe_id": "prod_S8obyQgyW9WfRa",  # this
        "is_active": False,  # this
        "type": ProductType.PACKAGE,
        "category": ProductCategory.IMAGE,
        "names": {
            "ru": Texts.GPT_IMAGE,
            "en": Texts.GPT_IMAGE,
            "es": Texts.GPT_IMAGE,
            "hi": Texts.GPT_IMAGE,
        },
        "descriptions": {
            "en": "Bring your vision to life with GPT-Image – your ideas, beautifully rendered by AI! 🧠🖼️",
            "ru": "Оживите своё видение с GPT-Image – ваши идеи, изящно воплощённые ИИ! 🧠🖼️",
            "es": "Da vida a tu visión con GPT-Image: ¡tus ideas bellamente plasmadas por la IA! 🧠🖼️",
            "hi": "GPT-Image के साथ अपने विचारों को जीवन दें – आपके आइडिया अब AI के जरिए खूबसूरती से साकार होंगे! 🧠🖼️",
        },
        "prices": {
            "RUB": 8,  # this
            "USD": 0.08,  # this
            "XTR": 8,  # this
        },
        "order": -1,  # this
        "details": {
            "quota": Quota.GPT_IMAGE,
            "support_photos": True,
        },
    }

    user_settings_gpt_image = {
        Model.GPT_IMAGE: {
            "version": gpt_image.Version.V1,
            "show_usage_quota": False,
            "size": gpt_image.user.settings.Size.SQUARE.value,
            "quality": gpt_image.user.settings.Quality.MEDIUM.value,
            "bg_transparent": gpt_image.user.settings.BgTransparent.NO.value,
            "compression": gpt_image.user.settings.Compression.NO.value,
        },
    }

    limits = {Quota.GPT_IMAGE: 0}

    # TODO add safe comment
    await down()
    await up(product_data, user_settings_gpt_image, limits)

    await send_message_to_admins_and_developers(bot, "<b>Database Migration Was Successful!</b> 🎉")
