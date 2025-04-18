import re
from urllib.parse import parse_qs, urlparse

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.database.main import firebase
from bot.database.models.common import UTM, Currency
from bot.database.models.product import ProductCategory
from bot.database.models.transaction import Transaction, TransactionType
from bot.database.operations.campaign.getters import get_campaign, get_campaign_by_name
from bot.database.operations.campaign.writers import write_campaign
from bot.database.operations.product.getters import get_product
from bot.database.operations.user.getters import get_users
from bot.keyboards.admin.admin import build_admin_keyboard
from bot.keyboards.admin.ads import (
    build_ads_create_choose_discount_keyboard,
    build_ads_create_choose_medium_keyboard,
    build_ads_create_choose_source_keyboard,
    build_ads_get_keyboard,
    build_ads_keyboard,
)
from bot.keyboards.common.common import build_cancel_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.states.admin.ads import Ads

ads_router = Router()


async def handle_ads(message: Message, user_id: str, state: FSMContext):
    await state.clear()

    user_language_code = await get_user_language(user_id, state.storage)

    await message.edit_text(
        text=get_localization(user_language_code).ADMIN_ADS_INFO,
        reply_markup=build_ads_keyboard(user_language_code),
    )


@ads_router.callback_query(lambda c: c.data.startswith("ads:"))
async def handle_ads_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    action = callback_query.data.split(":")[1]
    if action == "back":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_INFO,
            reply_markup=build_admin_keyboard(user_language_code),
        )

        await state.clear()
        return
    elif action == "create":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_ADS_CHOOSE_SOURCE,
            reply_markup=build_ads_create_choose_source_keyboard(user_language_code),
        )
    elif action == "get":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_ADS_SEND_LINK,
            reply_markup=build_ads_get_keyboard(user_language_code),
        )

        await state.set_state(Ads.waiting_for_link)


@ads_router.callback_query(lambda c: c.data.startswith("ads_create_choose_source:"))
async def handle_ads_create_choose_source_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    action = callback_query.data.split(":")[1]
    if action == "back":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_ADS_INFO,
            reply_markup=build_ads_keyboard(user_language_code),
        )
    else:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_ADS_CHOOSE_MEDIUM,
            reply_markup=build_ads_create_choose_medium_keyboard(user_language_code),
        )

        await state.update_data(campaign_source=action)


@ads_router.callback_query(lambda c: c.data.startswith("ads_create_choose_medium:"))
async def handle_ads_create_choose_source_selection_medium(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    action = callback_query.data.split(":")[1]
    if action == "back":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_ADS_INFO,
            reply_markup=build_ads_keyboard(user_language_code),
        )
    else:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_ADS_SEND_DISCOUNT,
            reply_markup=build_ads_create_choose_discount_keyboard(user_language_code),
        )

        await state.update_data(campaign_medium=action)
        await state.set_state(Ads.waiting_for_discount)


@ads_router.callback_query(lambda c: c.data.startswith("ads_create_choose_discount:"))
async def handle_ads_create_choose_discount_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    discount = int(callback_query.data.split(":")[1])
    await callback_query.message.edit_text(
        text=get_localization(user_language_code).ADMIN_ADS_SEND_NAME,
        reply_markup=build_cancel_keyboard(user_language_code),
    )

    await state.set_state(Ads.waiting_for_campaign_name)
    await state.update_data(campaign_discount=discount)


@ads_router.message(Ads.waiting_for_discount, F.text, ~F.text.startswith("/"))
async def ads_discount_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(
        str(message.from_user.id), state.storage
    )

    try:
        discount = int(message.text)

        if 1 <= discount <= 50:
            await message.answer(
                text=get_localization(user_language_code).ADMIN_ADS_SEND_NAME,
                reply_markup=build_cancel_keyboard(user_language_code),
            )

            await state.set_state(Ads.waiting_for_campaign_name)
            await state.update_data(campaign_discount=discount)
        else:
            raise ValueError
    except (TypeError, ValueError):
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


@ads_router.message(Ads.waiting_for_campaign_name, F.text, ~F.text.startswith("/"))
async def ads_campaign_name_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(
        str(message.from_user.id), state.storage
    )
    user_data = await state.get_data()

    campaign_name = message.text
    if re.match(r"^[a-zA-Z]+$", campaign_name):
        existed_campaign = await get_campaign_by_name(campaign_name)
        if existed_campaign:
            await message.reply(
                text=get_localization(user_language_code).ADMIN_ADS_VALUE_ERROR,
                reply_markup=build_cancel_keyboard(user_language_code),
                allow_sending_without_reply=True,
            )
            return

        await state.update_data(campaign_name=campaign_name)

        (
            campaign_source,
            campaign_medium,
            campaign_discount,
        ) = (
            user_data.get("campaign_source"),
            user_data.get("campaign_medium"),
            user_data.get("campaign_discount"),
        )
        utm = {
            UTM.SOURCE: campaign_source,
            UTM.MEDIUM: campaign_medium,
            UTM.CAMPAIGN: campaign_name,
        }

        campaign = await write_campaign(
            utm,
            campaign_discount,
        )

        await message.answer(
            text=f"1. {config.BOT_URL}?start=c-{campaign.id}\n"
            f"2. {config.BOT_URL}?start=c-{campaign.utm.get(UTM.CAMPAIGN)}",
        )
        await state.clear()
    else:
        await message.reply(
            text=get_localization(user_language_code).ADMIN_ADS_VALUE_ERROR,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


@ads_router.callback_query(lambda c: c.data.startswith("ads_create:"))
async def handle_ads_create_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    action = callback_query.data.split(":")[1]
    if action == "back":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_ADS_INFO,
            reply_markup=build_ads_keyboard(user_language_code),
        )

        await state.clear()


@ads_router.message(Ads.waiting_for_link, F.text, ~F.text.startswith("/"))
async def ads_link_sent(message: Message, state: FSMContext):
    parsed_url = urlparse(message.text)
    params = parse_qs(parsed_url.query)

    utm = [value for key, value in vars(UTM).items() if not key.startswith("__")]
    link_utm = {}

    start_param = params.get("start", [""])[0]
    sub_params = start_param.split("_")
    for sub_param in sub_params:
        if "-" not in sub_param:
            continue

        sub_param_key, sub_param_value = sub_param.split("-")
        if sub_param_key == "c":
            campaign = await get_campaign(sub_param_value)
            if not campaign:
                campaign = await get_campaign_by_name(sub_param_value)
            link_utm = campaign.utm
        elif sub_param_key in utm:
            link_utm[sub_param_key] = sub_param_value.lower()

    users = await get_users(
        utm=link_utm,
    )

    product_cache = {}

    nothing_users = 0
    text_users = 0
    summary_users = 0
    image_users = 0
    music_users = 0
    video_users = 0
    all_ai_users = 0
    clients = 0
    clients_income = 0
    for user in users:
        has_text_requests = False
        has_summary_requests = False
        has_image_requests = False
        has_music_requests = False
        has_video_requests = False
        has_purchases = False

        transactions_query = (
            firebase.db.collection(Transaction.COLLECTION_NAME)
            .where("user_id", "==", user.id)
            .order_by("created_at")
            .limit(config.BATCH_SIZE)
        )

        is_running = True
        last_doc = None

        while is_running:
            if last_doc:
                transactions_query = transactions_query.start_after(last_doc)

            docs = transactions_query.stream()

            count = 0
            async for doc in docs:
                count += 1

                transaction = Transaction(**doc.to_dict())

                if transaction.type == TransactionType.INCOME:
                    has_purchases = True
                    if transaction.currency == Currency.USD:
                        clients_income += transaction.clear_amount * 100
                    elif transaction.currency == Currency.XTR:
                        clients_income += transaction.clear_amount * 2
                    else:
                        clients_income += transaction.clear_amount
                elif transaction.type == TransactionType.EXPENSE:
                    if transaction.product_id not in product_cache:
                        transaction_product = await get_product(transaction.product_id)
                        product_cache[transaction.product_id] = transaction_product
                    else:
                        transaction_product = product_cache[transaction.product_id]
                    if transaction_product.category == ProductCategory.TEXT:
                        has_text_requests = True
                    elif transaction_product.category == ProductCategory.SUMMARY:
                        has_summary_requests = True
                    elif transaction_product.category == ProductCategory.IMAGE:
                        has_image_requests = True
                    elif transaction_product.category == ProductCategory.MUSIC:
                        has_music_requests = True
                    elif transaction_product.category == ProductCategory.VIDEO:
                        has_video_requests = True

            if count < config.BATCH_SIZE:
                is_running = False
                break

            last_doc = doc

        if all(
            [
                has_text_requests,
                has_summary_requests,
                has_image_requests,
                has_music_requests,
                has_video_requests,
            ]
        ):
            all_ai_users += 1
        elif any(
            [
                has_text_requests,
                has_summary_requests,
                has_image_requests,
                has_music_requests,
                has_video_requests,
            ]
        ):
            if has_text_requests:
                text_users += 1

            if has_summary_requests:
                summary_users += 1

            if has_image_requests:
                image_users += 1

            if has_music_requests:
                music_users += 1

            if has_video_requests:
                video_users += 1
        else:
            nothing_users += 1

        if has_purchases:
            clients += 1

    await message.answer(
        text=f"""
📯 <b>{campaign.id}</b>

• <b>{len(users)}</b> - Всего пришло
• <b>{nothing_users}</b> - Не писали ничего
• <b>{text_users}</b> - Сделали запрос в текстовой модели
• <b>{summary_users}</b> - Сделали запрос в резюме модели
• <b>{image_users}</b> - Сделали запрос в графической модели
• <b>{music_users}</b> - Сделали запрос в музыкальной модели
• <b>{video_users}</b> - Сделали запрос в видео модели
• <b>{all_ai_users}</b> - Сделали запрос во всех моделях
• <b>{clients}</b> - Купили на сумму {round(clients_income, 2)}₽
"""
    )

    await state.clear()
