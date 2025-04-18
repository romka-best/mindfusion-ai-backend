from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile

from bot.database.main import firebase
from bot.database.models.product import ProductCategory, ProductType
from bot.database.models.promo_code import PromoCodeType
from bot.database.models.subscription import SubscriptionPeriod
from bot.database.operations.product.getters import (
    get_active_products_by_product_type_and_category,
    get_product,
)
from bot.database.operations.promo_code.getters import get_promo_code_by_name
from bot.database.operations.promo_code.writers import write_promo_code
from bot.keyboards.admin.admin import build_admin_keyboard
from bot.keyboards.admin.promo_code import (
    build_create_promo_code_discount_keyboard,
    build_create_promo_code_keyboard,
    build_create_promo_code_package_keyboard,
    build_create_promo_code_subscription_keyboard,
)
from bot.keyboards.common.common import build_cancel_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.states.payment.promo_code import PromoCode

admin_promo_code_router = Router()


async def handle_create_promo_code(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(user_id, state.storage)

    await message.edit_text(
        text=get_localization(user_language_code).ADMIN_PROMO_CODE_INFO,
        reply_markup=build_create_promo_code_keyboard(user_language_code),
    )


@admin_promo_code_router.callback_query(
    lambda c: c.data.startswith("create_promo_code:")
)
async def handle_create_promo_code_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    promo_code_type = callback_query.data.split(":")[1]
    if promo_code_type == "back":
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_INFO,
            reply_markup=build_admin_keyboard(user_language_code),
        )

        return
    elif promo_code_type == PromoCodeType.SUBSCRIPTION:
        photo_path = f"payments/subscriptions_{user_language_code}.png"
        photo = await firebase.bucket.get_blob(photo_path)
        photo_link = firebase.get_public_url(photo.name)

        products = await get_active_products_by_product_type_and_category(
            ProductType.SUBSCRIPTION,
            ProductCategory.MONTHLY,
        )

        await callback_query.message.answer_photo(
            photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
            caption=get_localization(
                user_language_code
            ).ADMIN_PROMO_CODE_CHOOSE_SUBSCRIPTION,
            reply_markup=build_create_promo_code_subscription_keyboard(
                user_language_code, products
            ),
        )
    elif promo_code_type == PromoCodeType.PACKAGE:
        photo_path = f"payments/packages_{user_language_code}.png"
        photo = await firebase.bucket.get_blob(photo_path)
        photo_link = firebase.get_public_url(photo.name)

        products = await get_active_products_by_product_type_and_category(
            ProductType.PACKAGE
        )

        await callback_query.message.answer_photo(
            photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
            caption=get_localization(
                user_language_code
            ).ADMIN_PROMO_CODE_CHOOSE_PACKAGE,
            reply_markup=build_create_promo_code_package_keyboard(
                user_language_code, products
            ),
        )
    elif promo_code_type == PromoCodeType.DISCOUNT:
        await callback_query.message.answer(
            text=get_localization(user_language_code).ADMIN_PROMO_CODE_CHOOSE_DISCOUNT,
            reply_markup=build_create_promo_code_discount_keyboard(user_language_code),
        )

        await state.set_state(PromoCode.waiting_for_promo_code_discount)

    await callback_query.message.delete()


@admin_promo_code_router.callback_query(
    lambda c: c.data.startswith("create_promo_code_subscription:")
)
async def handle_create_promo_code_period_of_subscription_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    product_id = callback_query.data.split(":")[1]

    await callback_query.message.edit_caption(
        caption=get_localization(user_language_code).ADMIN_PROMO_CODE_CHOOSE_NAME,
        reply_markup=build_cancel_keyboard(user_language_code),
    )

    await state.set_state(PromoCode.waiting_for_promo_code_name)
    await state.update_data(
        promo_code_type=PromoCodeType.SUBSCRIPTION,
        promo_code_product_id=product_id,
    )


@admin_promo_code_router.callback_query(
    lambda c: c.data.startswith("create_promo_code_package:")
)
async def handle_create_promo_code_package_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    product_id = callback_query.data.split(":")[1]
    product = await get_product(product_id)

    await callback_query.message.edit_caption(
        caption=get_localization(user_language_code).package_choose_min(
            product.names.get(user_language_code)
        ),
        reply_markup=build_cancel_keyboard(user_language_code),
    )

    await state.update_data(promo_code_product_id=product_id)
    await state.set_state(PromoCode.waiting_for_promo_code_package_quantity)


@admin_promo_code_router.message(
    PromoCode.waiting_for_promo_code_package_quantity, ~F.text.startswith("/")
)
async def handle_create_promo_promo_code_package_quantity_sent(
    message: Message, state: FSMContext
):
    user_language_code = await get_user_language(
        str(message.from_user.id), state.storage
    )

    try:
        quantity = int(message.text)

        await message.answer(
            text=get_localization(user_language_code).ADMIN_PROMO_CODE_CHOOSE_NAME,
            reply_markup=build_cancel_keyboard(user_language_code),
        )

        await state.set_state(PromoCode.waiting_for_promo_code_name)
        await state.update_data(
            promo_code_type=PromoCodeType.PACKAGE,
            promo_code_package_quantity=quantity,
        )
    except (TypeError, ValueError):
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


@admin_promo_code_router.callback_query(
    lambda c: c.data.startswith("create_promo_code_discount:")
)
async def handle_create_promo_code_discount_selection(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.answer()

    user_language_code = await get_user_language(
        str(callback_query.from_user.id), state.storage
    )

    discount = int(callback_query.data.split(":")[1])
    await callback_query.message.answer(
        text=get_localization(user_language_code).ADMIN_PROMO_CODE_CHOOSE_NAME,
        reply_markup=build_cancel_keyboard(user_language_code),
    )

    await state.set_state(PromoCode.waiting_for_promo_code_name)
    await state.update_data(
        promo_code_type=PromoCodeType.DISCOUNT,
        promo_code_discount=discount,
    )


@admin_promo_code_router.message(
    PromoCode.waiting_for_promo_code_discount, ~F.text.startswith("/")
)
async def handle_create_promo_code_discount_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(
        str(message.from_user.id), state.storage
    )

    try:
        discount = int(message.text)

        if 1 <= discount <= 50:
            await message.answer(
                text=get_localization(user_language_code).ADMIN_PROMO_CODE_CHOOSE_NAME,
                reply_markup=build_cancel_keyboard(user_language_code),
            )

            await state.set_state(PromoCode.waiting_for_promo_code_name)
            await state.update_data(
                promo_code_type=PromoCodeType.DISCOUNT,
                promo_code_discount=discount,
            )
        else:
            raise ValueError
    except (TypeError, ValueError):
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


@admin_promo_code_router.message(
    PromoCode.waiting_for_promo_code_name, F.text, ~F.text.startswith("/")
)
async def promo_code_name_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(
        str(message.from_user.id), state.storage
    )

    promo_code_name = message.text.upper()
    typed_promo_code = await get_promo_code_by_name(promo_code_name)
    reply_markup = build_cancel_keyboard(user_language_code)
    if typed_promo_code:
        await message.reply(
            text=get_localization(
                user_language_code
            ).ADMIN_PROMO_CODE_NAME_EXISTS_ERROR,
            reply_markup=reply_markup,
            allow_sending_without_reply=True,
        )
    else:
        await message.reply(
            text=get_localization(user_language_code).ADMIN_PROMO_CODE_CHOOSE_DATE,
            reply_markup=reply_markup,
            allow_sending_without_reply=True,
        )

        await state.set_state(state=None)
        await state.update_data(promo_code_name=promo_code_name)
        await state.set_state(PromoCode.waiting_for_promo_code_date)


@admin_promo_code_router.message(
    PromoCode.waiting_for_promo_code_date, ~F.text.startswith("/")
)
async def promo_code_date_sent(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    try:
        user_data = await state.get_data()
        promo_code_until_date = datetime.strptime(message.text, "%d.%m.%Y")
        promo_code_name = user_data["promo_code_name"]
        promo_code_type = user_data["promo_code_type"]
        details = {}
        if promo_code_type == PromoCodeType.SUBSCRIPTION:
            details["product_id"] = user_data["promo_code_product_id"]
            details["subscription_period"] = SubscriptionPeriod.MONTH1
        elif promo_code_type == PromoCodeType.PACKAGE:
            details["product_id"] = user_data["promo_code_product_id"]
            details["package_quantity"] = user_data["promo_code_package_quantity"]
        elif promo_code_type == PromoCodeType.DISCOUNT:
            details["discount"] = int(user_data["promo_code_discount"])

        await write_promo_code(
            created_by_user_id=user_id,
            name=promo_code_name,
            type=promo_code_type,
            until=promo_code_until_date,
            details=details,
        )
        await message.answer(
            text=get_localization(user_language_code).ADMIN_PROMO_CODE_SUCCESS
        )

        await state.clear()
    except (TypeError, ValueError):
        await message.reply(
            text=get_localization(user_language_code).ADMIN_PROMO_CODE_DATE_VALUE_ERROR,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )
