from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database.main import firebase
from bot.database.models.common import PaymentMethod
from bot.database.models.package import PackageStatus
from bot.database.models.promo_code import PromoCodeType
from bot.database.models.subscription import SubscriptionStatus
from bot.database.operations.package.writers import write_package
from bot.database.operations.product.getters import get_product
from bot.database.operations.promo_code.getters import (
    get_promo_code_by_name,
    get_used_promo_code_by_user_id_and_promo_code_id,
)
from bot.database.operations.promo_code.writers import write_used_promo_code
from bot.database.operations.subscription.writers import write_subscription
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.creaters.create_package import create_package
from bot.helpers.creaters.create_subscription import create_subscription
from bot.keyboards.common.common import (
    build_buy_motivation_keyboard,
    build_cancel_keyboard,
)
from bot.locales.main import get_localization, get_user_language
from bot.states.payment.promo_code import PromoCode

promo_code_router = Router()


async def handle_promo_code(message: Message, user_id: str, state: FSMContext):
    await state.clear()

    user_language_code = await get_user_language(str(user_id), state.storage)

    await message.answer(
        text=get_localization(user_language_code).PROMO_CODE_INFO,
        reply_markup=build_cancel_keyboard(user_language_code),
    )

    await state.set_state(PromoCode.waiting_for_promo_code)


@promo_code_router.message(Command("promo_code"))
async def promo_code(message: Message, state: FSMContext):
    await handle_promo_code(message, str(message.from_user.id), state)


@promo_code_router.message(
    PromoCode.waiting_for_promo_code, F.text, ~F.text.startswith("/")
)
async def promo_code_sent(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    typed_promo_code = await get_promo_code_by_name(message.text.upper())
    if typed_promo_code:
        current_date = datetime.now(timezone.utc)
        if current_date <= typed_promo_code.until:
            used_promo_code = await get_used_promo_code_by_user_id_and_promo_code_id(
                user_id, typed_promo_code.id
            )
            if used_promo_code:
                await message.reply(
                    text=get_localization(
                        user_language_code
                    ).PROMO_CODE_ALREADY_USED_ERROR,
                    reply_markup=build_buy_motivation_keyboard(user_language_code),
                    allow_sending_without_reply=True,
                )

                await state.clear()
            else:
                if typed_promo_code.type == PromoCodeType.SUBSCRIPTION:
                    if not user.subscription_id:
                        subscription = await write_subscription(
                            None,
                            user_id,
                            typed_promo_code.details["product_id"],
                            typed_promo_code.details["subscription_period"],
                            SubscriptionStatus.WAITING,
                            user.currency,
                            0,
                            0,
                            PaymentMethod.GIFT,
                            "",
                        )

                        transaction = firebase.db.transaction()
                        await create_subscription(
                            transaction,
                            message.bot,
                            subscription.id,
                            subscription.user_id,
                            0,
                            "",
                            "",
                        )

                        await write_used_promo_code(user_id, typed_promo_code.id)
                        await message.reply(
                            text=get_localization(
                                user_language_code
                            ).PROMO_CODE_SUCCESS,
                            allow_sending_without_reply=True,
                        )

                        await state.clear()
                    else:
                        await message.reply(
                            text=get_localization(
                                user_language_code
                            ).PROMO_CODE_ALREADY_HAVE_SUBSCRIPTION,
                            reply_markup=build_cancel_keyboard(user_language_code),
                            allow_sending_without_reply=True,
                        )
                elif typed_promo_code.type == PromoCodeType.PACKAGE:
                    package_id = typed_promo_code.details["product_id"]
                    package_quantity = typed_promo_code.details["package_quantity"]

                    product = await get_product(package_id)

                    until_at = None
                    if product.details.get("is_recurring", False):
                        current_date = datetime.now(timezone.utc)
                        until_at = current_date + timedelta(
                            days=30 * int(package_quantity)
                        )

                    package = await write_package(
                        None,
                        user_id,
                        package_id,
                        PackageStatus.WAITING,
                        user.currency,
                        0,
                        0,
                        int(package_quantity),
                        PaymentMethod.GIFT,
                        None,
                        until_at,
                    )

                    transaction = firebase.db.transaction()
                    await create_package(
                        transaction,
                        package.id,
                        package.user_id,
                        0,
                        "",
                    )

                    await write_used_promo_code(user_id, typed_promo_code.id)
                    await message.reply(
                        text=get_localization(user_language_code).PROMO_CODE_SUCCESS,
                        allow_sending_without_reply=True,
                    )

                    await state.clear()
                elif typed_promo_code.type == PromoCodeType.DISCOUNT:
                    discount = int(typed_promo_code.details["discount"])
                    await update_user(
                        user_id,
                        {
                            "discount": discount,
                        },
                    )

                    await write_used_promo_code(user_id, typed_promo_code.id)
                    await message.reply(
                        text=get_localization(user_language_code).PROMO_CODE_SUCCESS,
                        allow_sending_without_reply=True,
                    )

                    await state.clear()
        else:
            await message.reply(
                text=get_localization(user_language_code).PROMO_CODE_EXPIRED_ERROR,
                reply_markup=build_buy_motivation_keyboard(user_language_code),
                allow_sending_without_reply=True,
            )

            await state.clear()
    else:
        await message.reply(
            text=get_localization(user_language_code).PROMO_CODE_NOT_FOUND_ERROR,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )
