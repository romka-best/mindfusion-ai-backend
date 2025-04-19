import asyncio
import calendar
from datetime import datetime, timezone, timedelta
from typing import Optional, cast

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from google.cloud.firestore_v1 import FieldFilter

from bot.config import config, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Currency
from bot.database.models.feedback import FeedbackStatus
from bot.database.models.game import GameType
from bot.database.models.generation import GenerationReaction
from bot.database.models.product import ProductType, ProductCategory, Product
from bot.database.models.subscription import SubscriptionStatus
from bot.database.models.transaction import Transaction, TransactionType, ServiceType
from bot.database.operations.feedback.getters import get_count_of_feedbacks
from bot.database.operations.game.getters import get_count_of_games, get_sum_of_games_reward
from bot.database.operations.generation.getters import get_count_of_generations
from bot.database.operations.product.getters import get_products
from bot.database.operations.promo_code.getters import get_count_of_used_promo_codes
from bot.database.operations.subscription.getters import get_count_of_subscriptions, get_subscription
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import (
    get_user,
    get_count_of_users,
    get_count_of_users_referred_by,
    get_count_of_users_campaign_by,
)
from bot.keyboards.admin.admin import build_admin_keyboard
from bot.keyboards.common.common import build_cancel_keyboard
from bot.states.admin.statistics import Statistics
from bot.keyboards.admin.statistics import (
    build_statistics_keyboard,
    build_statistics_write_transaction_keyboard,
    build_statistics_choose_service_keyboard,
    build_statistics_choose_currency_keyboard,
)
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode
from bot.utils.is_admin import is_admin

statistics_router = Router()


async def handle_statistics(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(str(user_id), state.storage)

    await message.edit_text(
        text=get_localization(user_language_code).ADMIN_STATISTICS_INFO,
        reply_markup=build_statistics_keyboard(user_language_code, is_admin(str(user_id))),
    )


async def handle_write_transaction(callback_query: CallbackQuery, language_code: LanguageCode):
    await callback_query.message.edit_text(
        text=get_localization(language_code).ADMIN_STATISTICS_WRITE_TRANSACTION,
        reply_markup=build_statistics_write_transaction_keyboard(language_code),
    )


async def get_zero():
    return 0


async def get_statistics_by_transactions_query(
    products: list[Product],
    text_products: dict[str, str],
    summary_products: dict[str, str],
    image_products: dict[str, str],
    music_products: dict[str, str],
    video_products: dict[str, str],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    subscription_users = {
        product.id: set() for product in products if product.type == ProductType.SUBSCRIPTION
    }
    subscription_users[ServiceType.FREE] = set()

    paid_users = set()
    activated_users = set()

    user_cache = {}

    default_transaction_nested_dict = {
        'SUCCESS': 0,
        'FAIL': 0,
        'EXAMPLE': 0,
        'ALL': 0,
        'BONUS': 0,
    }
    count_all_transactions = {
        product.id: default_transaction_nested_dict.copy() for product in products
    }
    count_all_transactions[ServiceType.FREE] = default_transaction_nested_dict.copy()
    count_all_transactions[ServiceType.SERVER] = default_transaction_nested_dict.copy()
    count_all_transactions[ServiceType.DATABASE] = default_transaction_nested_dict.copy()
    count_all_transactions[ServiceType.OTHER] = default_transaction_nested_dict.copy()

    count_income_money_total = 0
    count_income_money = {
        product.id: {Currency.RUB: 0, Currency.USD: 0, Currency.XTR: 0, 'net': 0} for product in products
        if product.id not in {
            ServiceType.SERVER,
            ServiceType.DATABASE,
        }
    }
    count_income_money.update({
        ServiceType.FREE: 0,
        ServiceType.OTHER: 0,
        'SUBSCRIPTION_ALL': 0,
        'PACKAGES_ALL': 0,
        'AVERAGE_PRICE': 0,
        'ALL': 0,
        'VAL': 0,
    })

    default_expense_money_nested_dict = {
        'AVERAGE_EXAMPLE_PRICE': 0,
        'EXAMPLE_ALL': 0,
        'AVERAGE_PRICE': 0,
        'TEXT': 0,
        'SUMMARY': 0,
        'IMAGE': 0,
        'MUSIC': 0,
        'VIDEO': 0,
        'ALL': 0,
    }
    count_expense_money = {
        product.id: default_expense_money_nested_dict.copy() for product in products
    }
    count_expense_money.update({
        ServiceType.FREE: default_expense_money_nested_dict.copy(),
        ServiceType.SERVER: default_expense_money_nested_dict.copy(),
        ServiceType.DATABASE: default_expense_money_nested_dict.copy(),
        ServiceType.OTHER: default_expense_money_nested_dict.copy(),
        'ALL': 0,
    })

    service_subscriptions = [
        product.id for product in products
        if product.type == ProductType.SUBSCRIPTION
    ]
    service_ai_models = [
        product.id for product in products
        if product.type == ProductType.PACKAGE and product.category != ProductCategory.OTHER
    ]
    service_packages = service_ai_models + [
        product.id for product in products
        if product.type == ProductType.PACKAGE and product.category == ProductCategory.OTHER
    ]

    transactions_query = firebase.db.collection(Transaction.COLLECTION_NAME).order_by('created_at')

    if start_date:
        transactions_query = transactions_query.where(filter=FieldFilter('created_at', '>=', start_date))
    if end_date:
        transactions_query = transactions_query.where(filter=FieldFilter('created_at', '<=', end_date))

    transactions_query = transactions_query.limit(config.BATCH_SIZE)

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

            if transaction.user_id not in user_cache:
                transaction_user = await get_user(transaction.user_id)
                user_cache[transaction.user_id] = transaction_user
            else:
                transaction_user = user_cache[transaction.user_id]

            if not transaction_user.subscription_id:
                subscription_users[ServiceType.FREE].add(transaction_user.id)
            else:
                transaction_user_subscription = await get_subscription(transaction_user.subscription_id)
                subscription_users[transaction_user_subscription.product_id].add(transaction_user.id)
            activated_users.add(transaction.user_id)

            if transaction.type == TransactionType.INCOME:
                count_income_money_total += 1
                transaction_net = transaction.clear_amount
                if transaction.currency == Currency.USD:
                    transaction_net *= 100
                elif transaction.currency == Currency.XTR:
                    transaction_net *= 2

                count_income_money[transaction.product_id][transaction.currency] += transaction.clear_amount
                count_income_money[transaction.product_id]['net'] += transaction_net
                if transaction.product_id in service_subscriptions:
                    count_income_money['SUBSCRIPTION_ALL'] += transaction_net
                elif transaction.product_id in service_packages:
                    count_income_money['PACKAGES_ALL'] += transaction_net
                count_income_money['ALL'] += transaction_net

                count_all_transactions[transaction.product_id]['BONUS'] += 1 \
                    if transaction.details.get('is_bonus', False) \
                    else 0

                if transaction_net > 0:
                    paid_users.add(transaction.user_id)
            elif transaction.type == TransactionType.EXPENSE:
                has_error = transaction.details.get('has_error', False)
                is_suggestion = transaction.details.get('is_suggestion', False)

                count_all_transactions[transaction.product_id]['SUCCESS'] += transaction.quantity \
                    if not has_error \
                    else 0
                count_all_transactions[transaction.product_id]['FAIL'] += transaction.quantity \
                    if has_error \
                    else 0
                count_all_transactions[transaction.product_id]['EXAMPLE'] += transaction.quantity \
                    if is_suggestion \
                    else 0
                count_all_transactions[transaction.product_id]['ALL'] += transaction.quantity

                count_expense_money[transaction.product_id]['AVERAGE_EXAMPLE_PRICE'] += transaction.amount \
                    if is_suggestion \
                    else 0
                count_expense_money[transaction.product_id]['EXAMPLE_ALL'] += transaction.amount \
                    if is_suggestion \
                    else 0
                count_expense_money[transaction.product_id]['AVERAGE_PRICE'] += transaction.amount \
                    if not is_suggestion \
                    else 0
                count_expense_money[transaction.product_id]['ALL'] += transaction.amount
                count_expense_money['ALL'] += transaction.amount

                is_super_admin = transaction.user_id == config.SUPER_ADMIN_ID
                if not is_super_admin:
                    for key, value in subscription_users.items():
                        if transaction.user_id in value:
                            if transaction.product_id in text_products:
                                count_expense_money[key]['TEXT'] += transaction.amount
                            elif transaction.product_id in summary_products:
                                count_expense_money[key]['SUMMARY'] += transaction.amount
                            elif transaction.product_id in image_products:
                                count_expense_money[key]['IMAGE'] += transaction.amount
                            elif transaction.product_id in music_products:
                                count_expense_money[key]['MUSIC'] += transaction.amount
                            elif transaction.product_id in video_products:
                                count_expense_money[key]['VIDEO'] += transaction.amount
                            count_expense_money[key]['ALL'] += transaction.amount
                            break

        if count < config.BATCH_SIZE:
            is_running = False
            break

        last_doc = doc

    for service in service_ai_models:
        successes = count_all_transactions[service]['SUCCESS']
        fails = count_all_transactions[service]['FAIL']
        examples = count_all_transactions[service]['EXAMPLE']
        total = successes + fails

        average_price = count_expense_money[service]['AVERAGE_PRICE']
        average_example_price = count_expense_money[service]['AVERAGE_EXAMPLE_PRICE']

        count_expense_money[service]['AVERAGE_PRICE'] = average_price / total \
            if total > 0 else 0
        count_expense_money[service]['AVERAGE_EXAMPLE_PRICE'] = average_example_price / examples \
            if examples > 0 else 0
    for key, value in subscription_users.items():
        count_expense_money[key]['AVERAGE_PRICE'] = (
            count_expense_money[key]['ALL'] / len(value)
        ) if len(value) else 0
    return (
        paid_users,
        activated_users,
        count_all_transactions,
        count_income_money_total,
        count_income_money,
        count_expense_money,
    )


async def handle_get_statistics(language_code: LanguageCode, period: str):
    current_date = datetime.now(timezone.utc)
    start_date = None
    end_date = None
    start_date_before = None
    end_date_before = None
    if period == 'day':
        start_date = (current_date - timedelta(days=1)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        end_date = (current_date - timedelta(days=1)).replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )
        period = start_date.strftime('%d.%m.%Y')

        start_date_before = start_date - timedelta(days=1)
        end_date_before = end_date - timedelta(days=1)
    elif period == 'week':
        start_date = (current_date - timedelta(days=current_date.weekday() + 7)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        end_date = (start_date + timedelta(days=6)).replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )
        period = f'{start_date.strftime("%d.%m.%Y")}-{end_date.strftime("%d.%m.%Y")}'

        start_date_before = start_date - timedelta(days=7)
        end_date_before = end_date - timedelta(days=7)
    elif period == 'month':
        first_day_of_last_month = current_date.replace(day=1) - timedelta(days=1)
        start_date = first_day_of_last_month.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        last_day_of_last_month = start_date + timedelta(
            days=calendar.monthrange(start_date.year, start_date.month)[1] - 1,
        )
        end_date = last_day_of_last_month.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )
        period = f'{start_date.strftime("%d.%m.%Y")}-{end_date.strftime("%d.%m.%Y")}'

        start_date_before = start_date - timedelta(days=calendar.monthrange(start_date.year, start_date.month)[1] - 1)
        end_date_before = start_date - timedelta(days=1)
        end_date_before = end_date_before.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )
    else:
        period = 'всё время'

    products = await get_products()
    products = sorted(products, key=lambda p: p.order)

    text_products = {
        product.id: product.names.get(language_code) for product in products
        if product.category == ProductCategory.TEXT
    }
    summary_products = {
        product.id: product.names.get(language_code) for product in products
        if product.category == ProductCategory.SUMMARY
    }
    image_products = {
        product.id: product.names.get(language_code) for product in products
        if product.category == ProductCategory.IMAGE
    }
    music_products = {
        product.id: product.names.get(language_code) for product in products
        if product.category == ProductCategory.MUSIC
    }
    video_products = {
        product.id: product.names.get(language_code) for product in products
        if product.category == ProductCategory.VIDEO
    }
    ai_products = text_products | summary_products | image_products | music_products | video_products

    text_package_products = {
        product.id: product.names.get(language_code) for product in products
        if product.type == ProductType.PACKAGE and product.category == ProductCategory.TEXT
    }
    summary_package_products = {
        product.id: product.names.get(language_code) for product in products
        if product.type == ProductType.PACKAGE and product.category == ProductCategory.SUMMARY
    }
    image_package_products = {
        product.id: product.names.get(language_code) for product in products
        if product.type == ProductType.PACKAGE and product.category == ProductCategory.IMAGE
    }
    music_package_products = {
        product.id: product.names.get(language_code) for product in products
        if product.type == ProductType.PACKAGE and product.category == ProductCategory.MUSIC
    }
    video_package_products = {
        product.id: product.names.get(language_code) for product in products
        if product.type == ProductType.PACKAGE and product.category == ProductCategory.VIDEO
    }

    package_products = text_package_products | summary_package_products | image_package_products | music_package_products | video_package_products

    tech_products = {
        product.id: product.names.get(language_code) for product in products
        if product.type == ProductType.PACKAGE and 'voice answers' in product.names.get(LanguageCode.EN, '').lower()
    }
    tech_products[ServiceType.SERVER] = get_localization(language_code).ADMIN_SERVER
    tech_products[ServiceType.DATABASE] = get_localization(language_code).ADMIN_DATABASE

    # users
    (
        count_all_users,
        count_all_users_before,
        count_blocked_users,
        count_blocked_users_before,
        count_referred_users,
        count_referred_users_before,
        count_campaign_users,
        count_campaign_users_before,
        count_english_users,
        count_english_users_before,
        count_russian_users,
        count_russian_users_before,
        count_spanish_users,
        count_spanish_users_before,
        count_hindi_users,
        count_hindi_users_before,
    ) = await asyncio.gather(
        # count_all_users
        get_count_of_users(
            start_date=start_date,
            end_date=end_date,
        ),
        # count_all_users_before
        get_count_of_users(
            start_date=start_date_before,
            end_date=end_date_before,
        ) if start_date_before and end_date_before else get_zero(),
        # count_blocked_users
        get_count_of_users(
            start_date=start_date,
            end_date=end_date,
            is_blocked=True,
        ),
        # count_blocked_users_before
        get_count_of_users(
            start_date=start_date_before,
            end_date=end_date_before,
            is_blocked=True,
        ) if start_date_before and end_date_before else get_zero(),
        # count_referred_users
        get_count_of_users_referred_by(
            start_date=start_date,
            end_date=end_date,
        ),
        # count_referred_users_before
        get_count_of_users_referred_by(
            start_date=start_date_before,
            end_date=end_date_before,
        ) if start_date_before and end_date_before else get_zero(),
        # count_campaign_users
        get_count_of_users_campaign_by(
            start_date=start_date,
            end_date=end_date,
        ),
        # count_campaign_users_before
        get_count_of_users_campaign_by(
            start_date=start_date_before,
            end_date=end_date_before,
        ) if start_date_before and end_date_before else get_zero(),
        # count_english_users
        get_count_of_users(
            start_date=start_date,
            end_date=end_date,
            language_code=LanguageCode.EN,
        ),
        # count_english_users_before
        get_count_of_users(
            start_date=start_date_before,
            end_date=end_date_before,
            language_code=LanguageCode.EN,
        ) if start_date_before and end_date_before else get_zero(),
        # count_russian_users
        get_count_of_users(
            start_date=start_date,
            end_date=end_date,
            language_code=LanguageCode.RU,
        ),
        # count_russian_users_before
        get_count_of_users(
            start_date=start_date_before,
            end_date=end_date_before,
            language_code=LanguageCode.RU,
        ) if start_date_before and end_date_before else get_zero(),
        # count_spanish_users
        get_count_of_users(
            start_date=start_date,
            end_date=end_date,
            language_code=LanguageCode.ES,
        ),
        # count_spanish_users_before
        get_count_of_users(
            start_date=start_date_before,
            end_date=end_date_before,
            language_code=LanguageCode.ES,
        ) if start_date_before and end_date_before else get_zero(),
        # count_hindi_users
        get_count_of_users(
            start_date=start_date,
            end_date=end_date,
            language_code=LanguageCode.HI,
        ),
        # count_hindi_users_before
        get_count_of_users(
            start_date=start_date_before,
            end_date=end_date_before,
            language_code=LanguageCode.HI,
        ) if start_date_before and end_date_before else get_zero(),
    )
    (
        count_other_users,
        count_other_users_before,
    ) = (
        count_all_users - (
            count_english_users + count_russian_users + count_spanish_users + count_hindi_users
        ),
        count_all_users_before - (
            count_english_users_before + count_russian_users_before + count_spanish_users_before + count_hindi_users_before
        ),
    )

    subscriptions = [
        product.id for product in products
        if product.type == ProductType.SUBSCRIPTION
    ]
    count_subscription_users = {}
    count_subscription_users_before = {}
    subscription_tasks = [
        get_count_of_subscriptions(
            start_date=start_date,
            end_date=end_date,
            product_id=subscription,
            statuses=[SubscriptionStatus.ACTIVE, SubscriptionStatus.CANCELED],
        ) if start_date and end_date else get_count_of_users(  # TODO
            subscription_id=subscription,
        ) for subscription in subscriptions
    ]
    subscription_before_tasks = [
        get_count_of_subscriptions(
            start_date=start_date_before,
            end_date=end_date_before,
            product_id=subscription,
            statuses=[SubscriptionStatus.ACTIVE, SubscriptionStatus.CANCELED],
        ) if start_date_before and end_date_before else get_zero() for subscription in subscriptions
    ]

    subscription_results, subscription_before_results = await asyncio.gather(
        asyncio.gather(*subscription_tasks),
        asyncio.gather(*subscription_before_tasks)
    )

    count_subscription_users[ServiceType.FREE] = 0
    count_subscription_users_before[ServiceType.FREE] = 0
    for subscription, count, count_before in zip(subscriptions, subscription_results, subscription_before_results):
        count_subscription_users[subscription] = count
        count_subscription_users_before[subscription] = count_before

    subscription_products = {
        '🆓 Бесплатные': [ServiceType.FREE],
    }
    for product in products:
        if product.type == ProductType.SUBSCRIPTION:
            product_name = product.names.get(language_code)
            if product_name in subscription_products:
                subscription_products[product_name].append(product.id)
            else:
                subscription_products[product_name] = [product.id]

    count_users = await get_count_of_users()
    count_subscription_users[ServiceType.FREE] = abs(
        count_users - sum(count_subscription_users.values())
    ) if count_subscription_users[ServiceType.FREE] == 0 \
        else count_subscription_users[ServiceType.FREE]
    count_subscription_users_before[ServiceType.FREE] = abs(
        count_users - sum(count_subscription_users_before.values())
    ) if count_subscription_users_before[ServiceType.FREE] == 0 \
        else count_subscription_users_before[ServiceType.FREE]

    # reactions
    products_with_reactions = {
        product.id: product.names.get(language_code) for product in products
        if product.details.get('has_reactions', False)
    }
    default_reactions_nested_dict = {
        GenerationReaction.LIKED: 0,
        GenerationReaction.DISLIKED: 0,
        GenerationReaction.NONE: 0,
    }
    count_reactions = {
        product_with_reactions: default_reactions_nested_dict.copy()
        for product_with_reactions in products_with_reactions
    }
    count_reactions_before = {
        product_with_reactions: default_reactions_nested_dict.copy()
        for product_with_reactions in products_with_reactions
    }

    for product_with_reactions in products_with_reactions:
        for generation_reaction in [GenerationReaction.LIKED, GenerationReaction.DISLIKED, GenerationReaction.NONE]:
            count_reactions[product_with_reactions][generation_reaction] = await get_count_of_generations(
                start_date=start_date,
                end_date=end_date,
                reaction=generation_reaction,
                product_id=product_with_reactions,
            )
            count_reactions_before[product_with_reactions][generation_reaction] = await get_count_of_generations(
                start_date=start_date,
                end_date=end_date,
                reaction=generation_reaction,
                product_id=product_with_reactions,
            ) if start_date_before and end_date_before else 0

    # transactions
    (
        paid_users,
        activated_users,
        count_all_transactions,
        count_income_money_total,
        count_income_money,
        count_expense_money,
    ) = await get_statistics_by_transactions_query(
        products=products,
        text_products=text_products,
        summary_products=summary_products,
        image_products=image_products,
        music_products=music_products,
        video_products=video_products,
        start_date=start_date,
        end_date=end_date,
    )
    (
        paid_users_before,
        activated_users_before,
        count_all_transactions_before,
        count_income_money_total_before,
        count_income_money_before,
        count_expense_money_before,
    ) = await get_statistics_by_transactions_query(
        products=products,
        text_products=text_products,
        summary_products=summary_products,
        image_products=image_products,
        music_products=music_products,
        video_products=video_products,
        start_date=start_date_before,
        end_date=end_date_before,
    )

    count_activated_users = len(activated_users)
    count_activated_users_before = len(activated_users_before)
    count_paid_users = len(paid_users)
    count_paid_users_before = len(paid_users_before)

    count_games = {
        key: 0 for key in list(GameType.__members__.keys())
    }
    count_games_before = {
        key: 0 for key in list(GameType.__members__.keys())
    }

    (
        count_games_reward,
        count_games_reward_before,
        count_games[GameType.BOWLING],
        count_games_before[GameType.BOWLING],
        count_games[GameType.SOCCER],
        count_games_before[GameType.SOCCER],
        count_games[GameType.BASKETBALL],
        count_games_before[GameType.BASKETBALL],
        count_games[GameType.DARTS],
        count_games_before[GameType.DARTS],
        count_games[GameType.DICE],
        count_games_before[GameType.DICE],
        count_games[GameType.CASINO],
        count_games_before[GameType.CASINO],
    ) = await asyncio.gather(
        get_sum_of_games_reward(
            start_date=start_date,
            end_date=end_date,
        ),
        get_sum_of_games_reward(
            start_date=start_date_before,
            end_date=end_date_before,
        ) if start_date_before and end_date_before else get_zero(),
        get_count_of_games(
            start_date=start_date,
            end_date=end_date,
            type=GameType.BOWLING,
        ),
        get_count_of_games(
            start_date=start_date_before,
            end_date=end_date_before,
            type=GameType.BOWLING,
        ) if start_date_before and end_date_before else get_zero(),
        get_count_of_games(
            start_date=start_date,
            end_date=end_date,
            type=GameType.SOCCER,
        ),
        get_count_of_games(
            start_date=start_date_before,
            end_date=end_date_before,
            type=GameType.SOCCER,
        ) if start_date_before and end_date_before else get_zero(),
        get_count_of_games(
            start_date=start_date,
            end_date=end_date,
            type=GameType.BASKETBALL,
        ),
        get_count_of_games(
            start_date=start_date_before,
            end_date=end_date_before,
            type=GameType.BASKETBALL,
        ) if start_date_before and end_date_before else get_zero(),
        get_count_of_games(
            start_date=start_date,
            end_date=end_date,
            type=GameType.DARTS,
        ),
        get_count_of_games(
            start_date=start_date_before,
            end_date=end_date_before,
            type=GameType.DARTS,
        ) if start_date_before and end_date_before else get_zero(),
        get_count_of_games(
            start_date=start_date,
            end_date=end_date,
            type=GameType.DICE,
        ),
        get_count_of_games(
            start_date=start_date_before,
            end_date=end_date_before,
            type=GameType.DICE,
        ) if start_date_before and end_date_before else get_zero(),
        get_count_of_games(
            start_date=start_date,
            end_date=end_date,
            type=GameType.CASINO,
        ),
        get_count_of_games(
            start_date=start_date_before,
            end_date=end_date_before,
            type=GameType.CASINO,
        ) if start_date_before and end_date_before else get_zero(),
    )

    count_activated_promo_codes = await get_count_of_used_promo_codes(start_date, end_date)
    count_activated_promo_codes_before = await get_count_of_used_promo_codes(start_date_before, end_date_before) \
        if start_date_before and end_date_before \
        else []

    # feedbacks
    all_feedbacks = await get_count_of_feedbacks(start_date, end_date)
    all_feedbacks_before = await get_count_of_feedbacks(start_date_before, end_date_before) \
        if start_date_before and end_date_before \
        else 0
    approved_feedbacks = await get_count_of_feedbacks(start_date, end_date, FeedbackStatus.APPROVED)
    approved_feedbacks_before = await get_count_of_feedbacks(
        start_date_before,
        end_date_before,
        FeedbackStatus.APPROVED
    ) if start_date_before and end_date_before else 0
    denied_feedbacks = await get_count_of_feedbacks(start_date, end_date, FeedbackStatus.DENIED)
    denied_feedbacks_before = await get_count_of_feedbacks(
        start_date_before,
        end_date_before,
        FeedbackStatus.DENIED
    ) if start_date_before and end_date_before else 0
    count_feedbacks = {
        FeedbackStatus.APPROVED: approved_feedbacks,
        FeedbackStatus.DENIED: denied_feedbacks,
        FeedbackStatus.WAITING: all_feedbacks - (approved_feedbacks + denied_feedbacks)
    }
    count_feedbacks_before = {
        FeedbackStatus.APPROVED: approved_feedbacks_before,
        FeedbackStatus.DENIED: denied_feedbacks_before,
        FeedbackStatus.WAITING: all_feedbacks_before - (approved_feedbacks_before + denied_feedbacks_before)
    }

    # credits
    count_credits = {
        'INVITE_FRIENDS': 0,
        'LEAVE_FEEDBACKS': 0,
        'PLAY_GAMES': 0,
        'ALL': 0,
    }
    count_credits_before = count_credits.copy()
    count_credits['INVITE_FRIENDS'] = 50 * count_referred_users
    count_credits_before['INVITE_FRIENDS'] = 50 * count_referred_users_before
    count_credits['LEAVE_FEEDBACKS'] = 25 * approved_feedbacks
    count_credits_before['LEAVE_FEEDBACKS'] = 25 * approved_feedbacks_before
    count_credits['PLAY_GAMES'] = count_games_reward
    count_credits_before['PLAY_GAMES'] = count_games_reward_before
    count_credits['ALL'] = (
        count_credits['INVITE_FRIENDS'] +
        count_credits['LEAVE_FEEDBACKS'] +
        count_credits['PLAY_GAMES']
    )
    count_credits_before['ALL'] = (
        count_credits_before['INVITE_FRIENDS'] +
        count_credits_before['LEAVE_FEEDBACKS'] +
        count_credits_before['PLAY_GAMES']
    )

    count_income_money['AVERAGE_PRICE'] = (
        count_income_money['ALL'] / count_income_money_total
    ) if count_income_money_total else 0
    count_income_money_before['AVERAGE_PRICE'] = (
        count_income_money_before['ALL'] / count_income_money_total_before
    ) if count_income_money_total_before else 0
    count_income_money['VAL'] = count_income_money['ALL'] - count_expense_money['ALL'] * 100
    count_income_money_before['VAL'] = count_income_money_before['ALL'] - count_expense_money_before['ALL'] * 100

    texts = {
        'users': get_localization(language_code).admin_statistics_users(
            period=period,
            subscription_products=subscription_products,
            count_all_users=count_all_users,
            count_all_users_before=count_all_users_before,
            count_activated_users=count_activated_users,
            count_activated_users_before=count_activated_users_before,
            count_referral_users=count_referred_users,
            count_referral_users_before=count_referred_users_before,
            count_campaign_users=count_campaign_users,
            count_campaign_users_before=count_campaign_users_before,
            count_english_users=count_english_users,
            count_english_users_before=count_english_users_before,
            count_russian_users=count_russian_users,
            count_russian_users_before=count_russian_users_before,
            count_spanish_users=count_spanish_users,
            count_spanish_users_before=count_spanish_users_before,
            count_hindi_users=count_hindi_users,
            count_hindi_users_before=count_hindi_users_before,
            count_other_users=count_other_users,
            count_other_users_before=count_other_users_before,
            count_paid_users=count_paid_users,
            count_paid_users_before=count_paid_users_before,
            count_blocked_users=count_blocked_users,
            count_blocked_users_before=count_blocked_users_before,
            count_subscription_users=count_subscription_users,
            count_subscription_users_before=count_subscription_users_before,
        ),
        'text_models': get_localization(language_code).admin_statistics_text_models(
            period=period,
            text_products=text_products,
            count_all_transactions=count_all_transactions,
            count_all_transactions_before=count_all_transactions_before,
        ),
        'summary_models': get_localization(language_code).admin_statistics_summary_models(
            period=period,
            summary_products=summary_products,
            count_all_transactions=count_all_transactions,
            count_all_transactions_before=count_all_transactions_before,
        ),
        'image_models': get_localization(language_code).admin_statistics_image_models(
            period=period,
            image_products=image_products,
            count_all_transactions=count_all_transactions,
            count_all_transactions_before=count_all_transactions_before,
        ),
        'music_models': get_localization(language_code).admin_statistics_music_models(
            period=period,
            music_products=music_products,
            count_all_transactions=count_all_transactions,
            count_all_transactions_before=count_all_transactions_before,
        ),
        'video_models': get_localization(language_code).admin_statistics_video_models(
            period=period,
            video_products=video_products,
            count_all_transactions=count_all_transactions,
            count_all_transactions_before=count_all_transactions_before,
        ),
        'reactions': get_localization(language_code).admin_statistics_reactions(
            period=period,
            products_with_reactions=products_with_reactions,
            count_reactions=count_reactions,
            count_reactions_before=count_reactions_before,
            count_feedbacks=count_feedbacks,
            count_feedbacks_before=count_feedbacks_before,
            count_games=count_games,
            count_games_before=count_games_before,
        ),
        'bonuses': get_localization(language_code).admin_statistics_bonuses(
            period=period,
            package_products=package_products,
            count_credits=count_credits,
            count_credits_before=count_credits_before,
            count_all_transactions=count_all_transactions,
            count_all_transactions_before=count_all_transactions_before,
            count_activated_promo_codes=count_activated_promo_codes,
            count_activated_promo_codes_before=count_activated_promo_codes_before,
        ),
        'ai_expenses': get_localization(language_code).admin_statistics_ai_expenses(
            period=period,
            ai_products=ai_products,
            count_expense_money=count_expense_money,
            count_expense_money_before=count_expense_money_before,
        ),
        'tech_expenses': get_localization(language_code).admin_statistics_tech_expenses(
            period=period,
            tech_products=tech_products,
            count_expense_money=count_expense_money,
            count_expense_money_before=count_expense_money_before,
        ),
        'user_expenses': get_localization(language_code).admin_statistics_user_expenses(
            period=period,
            subscription_products=subscription_products,
            count_expense_money=count_expense_money,
            count_expense_money_before=count_expense_money_before,
        ),
        'expenses': get_localization(language_code).admin_statistics_expenses(
            period=period,
            count_expense_money=count_expense_money,
            count_expense_money_before=count_expense_money_before,
        ),
        'incomes': get_localization(language_code).admin_statistics_incomes(
            period=period,
            subscription_products=subscription_products,
            package_products=package_products,
            count_income_money=count_income_money,
            count_income_money_before=count_income_money_before,
        ),
    }
    return texts


@statistics_router.callback_query(lambda c: c.data.startswith('statistics:'))
async def handle_statistics_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

    period = callback_query.data.split(':')[1]
    if period == 'back':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_INFO,
            reply_markup=build_admin_keyboard(user_language_code),
        )

        return
    elif period == 'write_transaction':
        await handle_write_transaction(callback_query, user_language_code)
        return

    processing_sticker = await callback_query.message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.THINKING),
    )
    processing_message = await callback_query.message.reply(
        text=get_localization(user_language_code).admin_statistics_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.typing(bot=callback_query.bot, chat_id=callback_query.message.chat.id):
        texts = await handle_get_statistics(user_language_code, period)
        for text in texts.values():
            await callback_query.message.answer(
                text=text,
                protect_content=True,
            )

    await processing_sticker.delete()
    await processing_message.delete()


@statistics_router.callback_query(lambda c: c.data.startswith('statistics_write_transaction:'))
async def handle_statistics_write_transaction_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    transaction_type = cast(TransactionType, callback_query.data.split(':')[1])
    if transaction_type == 'back':
        await handle_statistics(
            callback_query.message,
            str(callback_query.from_user.id),
            state,
        )
    else:
        user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

        products = await get_products()
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).ADMIN_STATISTICS_CHOOSE_SERVICE,
            reply_markup=build_statistics_choose_service_keyboard(user_language_code, products, transaction_type)
        )

        await state.update_data(transaction_type=transaction_type)


@statistics_router.callback_query(lambda c: c.data.startswith('statistics_choose_service:'))
async def handle_statistics_choose_service_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    service_id = callback_query.data.split(':')[1]
    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

    await callback_query.message.edit_text(
        text=get_localization(user_language_code).ADMIN_STATISTICS_CHOOSE_CURRENCY,
        reply_markup=build_statistics_choose_currency_keyboard(user_language_code)
    )

    await state.set_state(Statistics.waiting_for_statistics_service_quantity)
    await state.update_data(service_id=service_id)


@statistics_router.callback_query(lambda c: c.data.startswith('statistics_choose_currency:'))
async def handle_statistics_choose_currency_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    currency = callback_query.data.split(':')[1]
    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

    await callback_query.message.edit_text(
        text=get_localization(user_language_code).ADMIN_STATISTICS_SERVICE_QUANTITY,
        reply_markup=build_cancel_keyboard(user_language_code)
    )

    await state.set_state(Statistics.waiting_for_statistics_service_quantity)
    await state.update_data(currency=currency)


@statistics_router.message(Statistics.waiting_for_statistics_service_quantity, ~F.text.startswith('/'))
async def statistics_service_quantity_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(str(message.from_user.id), state.storage)

    try:
        quantity = int(message.text)
        if quantity < 1:
            await message.answer(
                text=get_localization(user_language_code).PACKAGE_QUANTITY_MIN_ERROR,
                reply_markup=build_cancel_keyboard(user_language_code),
            )
        else:
            await message.answer(
                text=get_localization(user_language_code).ADMIN_STATISTICS_SERVICE_AMOUNT,
                reply_markup=build_cancel_keyboard(user_language_code),
            )

            await state.update_data(service_quantity=quantity)
            await state.set_state(Statistics.waiting_for_statistics_service_amount)
    except (TypeError, ValueError):
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


@statistics_router.message(Statistics.waiting_for_statistics_service_amount, ~F.text.startswith('/'))
async def statistics_service_amount_sent(message: Message, state: FSMContext):
    user_language_code = await get_user_language(str(message.from_user.id), state.storage)

    try:
        amount = float(message.text)
        if amount < 0:
            await message.answer(
                text=get_localization(user_language_code).PACKAGE_QUANTITY_MIN_ERROR,
                reply_markup=build_cancel_keyboard(user_language_code),
            )
        else:
            await message.answer(
                text=get_localization(user_language_code).ADMIN_STATISTICS_SERVICE_DATE,
                reply_markup=build_cancel_keyboard(user_language_code),
            )

            await state.update_data(service_amount=amount)
            await state.set_state(Statistics.waiting_for_statistics_service_date)
    except (TypeError, ValueError):
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


@statistics_router.message(Statistics.waiting_for_statistics_service_date, ~F.text.startswith('/'))
async def statistics_service_date_sent(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    try:
        user_data = await state.get_data()
        service_date = datetime.strptime(message.text, '%d.%m.%Y')
        service_amount = user_data['service_amount']
        service_quantity = user_data['service_quantity']
        service_id = user_data['service_id']
        transaction_type = user_data['transaction_type']
        currency = user_data['currency']

        await write_transaction(
            user_id=user_id,
            type=transaction_type,
            product_id=service_id,
            amount=service_amount,
            clear_amount=service_amount,
            currency=currency,
            quantity=service_quantity,
            created_at=service_date,
        )
        await message.answer(text=get_localization(user_language_code).ADMIN_STATISTICS_WRITE_TRANSACTION_SUCCESSFUL)

        await state.clear()
    except (TypeError, ValueError):
        await message.reply(
            text=get_localization(user_language_code).ADMIN_STATISTICS_SERVICE_DATE_VALUE_ERROR,
            reply_markup=build_cancel_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )
