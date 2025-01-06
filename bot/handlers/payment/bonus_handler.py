import asyncio
from datetime import datetime, timezone, timedelta
from typing import cast

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, URLInputFile
from google.cloud.firestore_v1 import Increment

from bot.config import config, MessageEffect
from bot.database.main import firebase
from bot.database.models.common import Currency, PaymentMethod
from bot.database.models.game import GameType, GameStatus
from bot.database.models.package import PackageStatus
from bot.database.models.product import Product, ProductType, ProductCategory
from bot.database.models.transaction import TransactionType
from bot.database.operations.feedback.getters import get_count_of_approved_feedbacks_by_user_id
from bot.database.operations.game.getters import get_count_of_games_by_user_id
from bot.database.operations.game.writers import write_game
from bot.database.operations.package.writers import write_package
from bot.database.operations.product.getters import get_product, get_active_products_by_product_type_and_category
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user, get_count_of_users_by_referral
from bot.database.operations.user.updaters import update_user
from bot.handlers.common.feedback_handler import handle_feedback
from bot.handlers.common.info_handler import handle_info_selection
from bot.keyboards.payment.bonus import (
    build_bonus_keyboard,
    build_bonus_play_game_keyboard,
    build_bonus_cash_out_keyboard,
    build_bonus_play_game_chosen_keyboard,
)
from bot.keyboards.common.common import build_cancel_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode
from bot.states.payment.bonus import Bonus

bonus_router = Router()


@bonus_router.message(Command('bonus'))
async def bonus(message: Message, state: FSMContext):
    await state.clear()

    await handle_bonus(message, str(message.from_user.id), state)


async def handle_bonus(message: Message, user_id: str, state: FSMContext):
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)
    count_of_referred_users = await get_count_of_users_by_referral(user_id)
    count_of_feedbacks = await get_count_of_approved_feedbacks_by_user_id(user_id)
    count_of_games = await get_count_of_games_by_user_id(user_id)

    photo_path = f'payments/packages_{user_language_code}.png'
    photo = await firebase.bucket.get_blob(photo_path)
    photo_link = firebase.get_public_url(photo.name)

    text = get_localization(user_language_code).bonus_info(
        user_id,
        user.balance,
        count_of_referred_users,
        count_of_feedbacks,
        count_of_games,
    )
    reply_markup = build_bonus_keyboard(user_language_code, user_id)
    await message.answer_photo(
        photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
        caption=text,
        reply_markup=reply_markup,
    )


@bonus_router.callback_query(lambda c: c.data.startswith('bonus:'))
async def handle_bonus_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]
    if action == 'leave_feedback':
        await handle_feedback(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'play_game':
        user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

        reply_markup = build_bonus_play_game_keyboard(user_language_code)
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).BONUS_PLAY_GAME_CHOOSE,
            reply_markup=reply_markup,
        )
    elif action == 'cash_out':
        await handle_bonus_cash_out(callback_query.message, str(callback_query.from_user.id), state)


async def handle_bonus_cash_out(message: Message, user_id: str, state: FSMContext, page=0):
    user_language_code = await get_user_language(user_id, state.storage)

    if page == 0:
        product_category = ProductCategory.TEXT
    elif page == 1:
        product_category = ProductCategory.SUMMARY
    elif page == 2:
        product_category = ProductCategory.IMAGE
    elif page == 3:
        product_category = ProductCategory.MUSIC
    elif page == 4:
        product_category = ProductCategory.VIDEO
    elif page == 5:
        product_category = ProductCategory.OTHER
    else:
        product_category = None

    products = await get_active_products_by_product_type_and_category(
        ProductType.PACKAGE,
        product_category,
    )

    text = get_localization(user_language_code).BONUS_CHOOSE_PACKAGE
    reply_markup = build_bonus_cash_out_keyboard(user_language_code, products, page)
    await message.edit_caption(
        caption=text,
        reply_markup=reply_markup,
    )


@bonus_router.callback_query(lambda c: c.data.startswith('bonus_play_game:'))
async def handle_bonus_play_game_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    game_type = cast(GameType, callback_query.data.split(':')[1])
    reply_markup = build_bonus_play_game_chosen_keyboard(user_language_code, game_type)
    if game_type == GameType.BOWLING:
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).BONUS_PLAY_BOWLING_GAME_INFO,
            reply_markup=reply_markup,
        )
    elif game_type == GameType.SOCCER:
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).BONUS_PLAY_SOCCER_GAME_INFO,
            reply_markup=reply_markup,
        )
    elif game_type == GameType.BASKETBALL:
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).BONUS_PLAY_BASKETBALL_GAME_INFO,
            reply_markup=reply_markup,
        )
    elif game_type == GameType.DARTS:
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).BONUS_PLAY_DARTS_GAME_INFO,
            reply_markup=reply_markup,
        )
    elif game_type == GameType.DICE:
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).BONUS_PLAY_DICE_GAME_INFO,
            reply_markup=reply_markup,
        )
    elif game_type == GameType.CASINO:
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).BONUS_PLAY_CASINO_GAME_INFO,
            reply_markup=reply_markup,
        )
    else:
        user = await get_user(user_id)

        count_of_referred_users = await get_count_of_users_by_referral(user_id)
        count_of_feedbacks = await get_count_of_approved_feedbacks_by_user_id(user_id)
        count_of_games = await get_count_of_games_by_user_id(user_id)

        text = get_localization(user_language_code).bonus_info(
            user_id,
            user.balance,
            count_of_referred_users,
            count_of_feedbacks,
            count_of_games,
        )
        reply_markup = build_bonus_keyboard(user_language_code, user_id)
        await callback_query.message.edit_caption(
            caption=text,
            reply_markup=reply_markup,
        )


async def send_game_status_after_timeout(
    bot: Bot,
    chat_id: int,
    reply_to_message_id: int,
    language_code: LanguageCode,
    won: bool,
):
    await asyncio.sleep(3)

    text = get_localization(language_code).BONUS_PLAY_GAME_WON if won else get_localization(language_code).BONUS_PLAY_GAME_LOST

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_to_message_id=reply_to_message_id,
        allow_sending_without_reply=True,
        message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.CONGRATS) if won else None,
    )


@bonus_router.callback_query(lambda c: c.data.startswith('bonus_play_game_chosen:'))
async def handle_bonus_play_game_chosen_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    game_type = cast(GameType, callback_query.data.split(':')[1])
    if game_type == 'back':
        reply_markup = build_bonus_play_game_keyboard(user_language_code)
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).BONUS_PLAY_GAME_CHOOSE,
            reply_markup=reply_markup,
        )
        return

    current_date = datetime.now(timezone.utc)
    current_date_beginning = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    count_of_games = await get_count_of_games_by_user_id(user_id, current_date_beginning)
    if count_of_games > 0:
        await callback_query.message.answer(
            text=get_localization(user_language_code).bonus_play_game_reached_limit(),
        )
        return

    final_credits = 0
    if game_type == GameType.BOWLING:
        final_credits = (await callback_query.message.answer_dice('🎳')).dice.value
    elif game_type == GameType.SOCCER:
        won_credits = (await callback_query.message.answer_dice('⚽️')).dice.value
        if won_credits > 2:
            final_credits = 5
    elif game_type == GameType.BASKETBALL:
        won_credits = (await callback_query.message.answer_dice('🏀')).dice.value
        if won_credits > 3:
            final_credits = 10
    elif game_type == GameType.DARTS:
        won_credits = (await callback_query.message.answer_dice('🎯')).dice.value
        if won_credits == 6:
            final_credits = 15
    elif game_type == GameType.DICE:
        won_credits = (await callback_query.message.answer_dice('🎲')).dice.value
        user_choice = int(callback_query.data.split(':')[2])
        if won_credits == user_choice:
            final_credits = 20
    elif game_type == GameType.CASINO:
        won_credits = (await callback_query.message.answer_dice('🎰')).dice.value
        if won_credits in [1, 22, 43]:
            final_credits = 50
        elif won_credits == 64:
            final_credits = 100

    game_status = GameStatus.WON if final_credits > 0 else GameStatus.LOST
    await write_game(user_id, game_type, game_status, final_credits)

    if game_status == GameStatus.WON:
        await update_user(user_id, {
            'balance': Increment(final_credits),
        })

        asyncio.create_task(
            send_game_status_after_timeout(
                bot=callback_query.bot,
                chat_id=callback_query.message.chat.id,
                reply_to_message_id=callback_query.message.message_id,
                language_code=user_language_code,
                won=True,
            )
        )
    else:
        asyncio.create_task(
            send_game_status_after_timeout(
                bot=callback_query.bot,
                chat_id=callback_query.message.chat.id,
                reply_to_message_id=callback_query.message.message_id,
                language_code=user_language_code,
                won=False,
            )
        )


@bonus_router.callback_query(lambda c: c.data.startswith('bonus_cash_out:'))
async def handle_bonus_cash_out_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    product_id = callback_query.data.split(':')[1]
    if product_id == 'page':
        return
    elif (
        product_id == ProductCategory.TEXT or
        product_id == ProductCategory.SUMMARY or
        product_id == ProductCategory.IMAGE or
        product_id == ProductCategory.MUSIC or
        product_id == ProductCategory.VIDEO
    ):
        await handle_info_selection(callback_query, state, product_id)
    elif product_id == 'next' or product_id == 'prev':
        page = int(callback_query.data.split(':')[2])
        await handle_bonus_cash_out(callback_query.message, str(callback_query.from_user.id), state, page)
    elif product_id == 'back':
        user = await get_user(user_id)
        count_of_referred_users = await get_count_of_users_by_referral(user_id)
        count_of_feedbacks = await get_count_of_approved_feedbacks_by_user_id(user_id)
        count_of_games = await get_count_of_games_by_user_id(user_id)

        text = get_localization(user_language_code).bonus_info(
            user_id,
            user.balance,
            count_of_referred_users,
            count_of_feedbacks,
            count_of_games,
        )
        reply_markup = build_bonus_keyboard(user_language_code, user_id)
        await callback_query.message.edit_caption(
            caption=text,
            reply_markup=reply_markup,
        )
    else:
        product = await get_product(product_id)
        message = get_localization(user_language_code).package_choose_min(product.names.get(user_language_code))

        reply_markup = build_cancel_keyboard(user_language_code)
        await callback_query.message.edit_caption(caption=message, reply_markup=reply_markup)

        await state.update_data(product_id=product_id)
        await state.set_state(Bonus.waiting_for_package_quantity)


@bonus_router.message(Bonus.waiting_for_package_quantity, ~F.text.startswith('/'))
async def quantity_of_bonus_package_sent(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    try:
        user_data = await state.get_data()
        package_product_id = user_data['product_id']
        package_product_quantity = int(message.text)

        product = await get_product(package_product_id)

        price = float(Product.get_discount_price(
            ProductType.PACKAGE,
            package_product_quantity,
            product.prices.get(Currency.XTR),
            Currency.XTR,
            0,
        ))
        if price > user.balance:
            reply_markup = build_cancel_keyboard(user_language_code)
            await message.reply(
                text=get_localization(user_language_code).PACKAGE_QUANTITY_MAX_ERROR,
                reply_markup=reply_markup,
                allow_sending_without_reply=True,
            )
        else:
            user.balance -= price
            user.additional_usage_quota[product.details.get('quota')] += package_product_quantity
            until_at = None
            if product.details.get('is_recurring', False):
                current_date = datetime.now(timezone.utc)
                until_at = current_date + timedelta(days=30 * package_product_quantity)
            package = await write_package(
                None,
                user_id,
                product.id,
                PackageStatus.SUCCESS,
                user.currency,
                0,
                0,
                package_product_quantity,
                PaymentMethod.GIFT,
                None,
                until_at,
            )

            await write_transaction(
                user_id=user_id,
                type=TransactionType.INCOME,
                product_id=package.product_id,
                amount=0,
                clear_amount=0,
                currency=user.currency,
                quantity=package_product_quantity,
                details={
                    'payment_method': PaymentMethod.GIFT,
                    'package_id': package.id,
                    'provider_payment_charge_id': '',
                    'is_bonus': True,
                },
            )
            await update_user(user_id, {
                'balance': user.balance,
                'additional_usage_quota': user.additional_usage_quota,
            })

            await message.reply(
                text=get_localization(user_language_code).BONUS_ACTIVATED_SUCCESSFUL,
                allow_sending_without_reply=True,
            )

            await state.clear()
    except (TypeError, ValueError):
        reply_markup = build_cancel_keyboard(user_language_code)
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=reply_markup,
            allow_sending_without_reply=True,
        )
