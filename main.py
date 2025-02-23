import asyncio
import logging
import os
import re
import traceback
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from functools import partial

import uvicorn
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import (
    TelegramNetworkError,
    TelegramForbiddenError,
    TelegramRetryAfter,
    TelegramBadRequest,
    TelegramServerError,
)
from aiogram.types import Update
from aiohttp import ClientOSError, ClientTimeout
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from redis.backoff import FullJitterBackoff
from redis.retry import Retry
from redis.exceptions import ConnectionError

from bot.config import config
from bot.database.main import firebase
from bot.handlers.admin.admin_handler import admin_router
from bot.handlers.admin.ads_handler import ads_router
from bot.handlers.admin.ban_handler import ban_router
from bot.handlers.admin.blast_handler import blast_router
from bot.handlers.admin.catalog_handler import admin_catalog_router
from bot.handlers.admin.face_swap_handler import admin_face_swap_router
from bot.handlers.admin.promo_code_handler import admin_promo_code_router
from bot.handlers.admin.statistics_handler import statistics_router
from bot.handlers.ai.chat_gpt_handler import chat_gpt_router
from bot.handlers.ai.claude_handler import claude_router
from bot.handlers.ai.dalle_handler import dall_e_router
from bot.handlers.ai.deep_seek_handler import deep_seek_router
from bot.handlers.ai.eightify_handler import eightify_router
from bot.handlers.ai.face_swap_handler import face_swap_router
from bot.handlers.ai.flux_handler import flux_router
from bot.handlers.ai.gemini_handler import gemini_router
from bot.handlers.ai.gemini_video_handler import gemini_video_router
from bot.handlers.ai.grok_handler import grok_router
from bot.handlers.ai.kling_handler import kling_router
from bot.handlers.ai.luma_handler import luma_router
from bot.handlers.ai.midjourney_handler import midjourney_router
from bot.handlers.ai.model_handler import model_router
from bot.handlers.ai.music_gen_handler import music_gen_router
from bot.handlers.ai.perplexity_handler import perplexity_router
from bot.handlers.ai.photoshop_ai_handler import photoshop_ai_router
from bot.handlers.ai.pika_handler import pika_router
from bot.handlers.ai.recraft_handler import recraft_router
from bot.handlers.ai.runway_handler import runway_router
from bot.handlers.ai.stable_diffusion_handler import stable_diffusion_router
from bot.handlers.ai.suno_handler import suno_router
from bot.handlers.common.catalog_handler import catalog_router
from bot.handlers.common.common_handler import common_router
from bot.handlers.common.document_handler import document_router
from bot.handlers.common.feedback_handler import feedback_router
from bot.handlers.common.info_handler import info_router
from bot.handlers.common.maintenance_handler import maintenance_router
from bot.handlers.common.photo_handler import photo_router
from bot.handlers.common.profile_handler import profile_router
from bot.handlers.common.sticker_handler import sticker_router
from bot.handlers.common.text_handler import text_router
from bot.handlers.common.video_handler import video_router
from bot.handlers.common.voice_handler import voice_router
from bot.handlers.payment.bonus_handler import bonus_router
from bot.handlers.payment.payment_handler import payment_router
from bot.handlers.payment.promo_code_handler import promo_code_router
from bot.handlers.settings.language_handler import language_router
from bot.handlers.settings.settings_handler import settings_router
from bot.helpers.billing.check_waiting_payments import check_waiting_payments
from bot.helpers.billing.update_daily_expenses import update_daily_expenses
from bot.helpers.checkers.check_unresolved_requests import check_unresolved_requests
from bot.helpers.getters.get_user_id_from_telegram_update import get_user_id_from_telegram_update
from bot.helpers.handlers.handle_big_file import handle_big_file
from bot.helpers.handlers.handle_forbidden_error import handle_forbidden_error
from bot.helpers.handlers.handle_kling_webhook import handle_kling_webhook
from bot.helpers.handlers.handle_luma_webhook import handle_luma_webhook
from bot.helpers.handlers.handle_midjourney_webhook import handle_midjourney_webhook
from bot.helpers.handlers.handle_network_error import handle_network_error
from bot.helpers.handlers.handle_pika_webhook import handle_pika_webhook
from bot.helpers.handlers.handle_replicate_webhook import handle_replicate_webhook
from bot.helpers.handlers.handle_stripe_webhook import handle_stripe_webhook
from bot.helpers.handlers.handle_suno_webhook import handle_suno_webhook
from bot.helpers.handlers.handle_yookassa_webhook import handle_yookassa_webhook
from bot.helpers.notifiers.notify_admins_about_error import notify_admins_about_error
from bot.helpers.senders.send_statistics import send_statistics
from bot.helpers.setters.set_commands import set_commands
from bot.helpers.setters.set_description import set_description
from bot.helpers.updaters.update_daily_limits import update_daily_limits
from bot.locales.main import get_localization
from bot.middlewares.AuthMiddleware import AuthMessageMiddleware, AuthCallbackQueryMiddleware
from bot.middlewares.LoggingMiddleware import LoggingMessageMiddleware, LoggingCallbackQueryMiddleware
from bot.utils.migrate import migrate

WEBHOOK_BOT_PATH = f'/bot/{config.BOT_TOKEN.get_secret_value()}'
WEBHOOK_YOOKASSA_PATH = '/payment/yookassa'
WEBHOOK_STRIPE_PATH = '/payment/stripe'
WEBHOOK_REPLICATE_PATH = config.WEBHOOK_REPLICATE_PATH
WEBHOOK_MIDJOURNEY_PATH = config.WEBHOOK_MIDJOURNEY_PATH
WEBHOOK_SUNO_PATH = config.WEBHOOK_SUNO_PATH
WEBHOOK_KLING_PATH = config.WEBHOOK_KLING_PATH
WEBHOOK_LUMA_PATH = config.WEBHOOK_LUMA_PATH
WEBHOOK_PIKA_PATH = config.WEBHOOK_PIKA_PATH

WEBHOOK_BOT_URL = config.WEBHOOK_URL + WEBHOOK_BOT_PATH

WEBHOOK_ADDITIONAL_BOTS_PATHS = [
    f'/bot/{additional_bot_token.get_secret_value()}' for additional_bot_token in config.ADDITIONAL_BOT_TOKENS
]

bot = Bot(
    token=config.BOT_TOKEN.get_secret_value(),
    session=AiohttpSession(
        timeout=ClientTimeout(
            total=600,
            sock_connect=60,
        ),
    ),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        allow_sending_without_reply=True,
    ),
)
storage = RedisStorage.from_url(config.REDIS_URL, {
    'socket_keepalive': True,
    'health_check_interval': 30,
    'retry_on_timeout': True,
    'retry': Retry(FullJitterBackoff(cap=5, base=1), 5),
})
dp = Dispatcher(
    storage=storage,
    sm_strategy=FSMStrategy.GLOBAL_USER,
    maintenance_mode=False,
)

additional_bots = [
    Bot(
        token=additional_bot_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            allow_sending_without_reply=True,
        ),
    ) for additional_bot_token in config.ADDITIONAL_BOT_TOKENS
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_BOT_URL:
        await bot.set_webhook(url=WEBHOOK_BOT_URL)

    dp.include_routers(
        maintenance_router,
        common_router,
        info_router,
        catalog_router,
        feedback_router,
        language_router,
        model_router,
        payment_router,
        profile_router,
        promo_code_router,
        admin_router,
        admin_catalog_router,
        admin_face_swap_router,
        admin_promo_code_router,
        ads_router,
        ban_router,
        bonus_router,
        blast_router,
        settings_router,
        statistics_router,
        chat_gpt_router,
        claude_router,
        gemini_router,
        grok_router,
        deep_seek_router,
        perplexity_router,
        eightify_router,
        gemini_video_router,
        dall_e_router,
        midjourney_router,
        stable_diffusion_router,
        flux_router,
        recraft_router,
        face_swap_router,
        photoshop_ai_router,
        music_gen_router,
        suno_router,
        kling_router,
        runway_router,
        luma_router,
        pika_router,
        document_router,
        photo_router,
        video_router,
        sticker_router,
        voice_router,
        text_router,
    )

    dp.message.middleware(LoggingMessageMiddleware())
    dp.callback_query.middleware(LoggingCallbackQueryMiddleware())
    dp.message.middleware(AuthMessageMiddleware())
    dp.callback_query.middleware(AuthCallbackQueryMiddleware())

    await firebase.init()
    yield
    await bot.session.close()
    await storage.close()
    await firebase.close()


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_BOT_PATH)
async def bot_webhook(update: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(handle_update, update)


async def delayed_handle_update(update: Update, timeout: int):
    await asyncio.sleep(timeout)

    try:
        await dp.feed_update(bot=bot, update=update)
    except (ConnectionResetError, OSError, ClientOSError, ConnectionError, TelegramServerError, TelegramNetworkError):
        user_id = get_user_id_from_telegram_update(update)
        await handle_network_error(bot, user_id)
    except TelegramForbiddenError:
        await handle_forbidden_error(update)
    except TelegramRetryAfter as e:
        if (
            update.callback_query and
            update.callback_query.data and
            update.callback_query.data.startswith('blast_confirmation:')
        ):
            logging.warning(e)
        else:
            logging.error(f'Error in bot_delayed_webhook telegram retry after: {e}')
            asyncio.create_task(delayed_handle_update(update, e.retry_after + 30))
    except TelegramBadRequest as e:
        if e.message.startswith('Bad Request: message can\'t be deleted for everyone'):
            logging.warning(e)
        elif e.message.startswith('Bad Request: message to delete not found'):
            logging.warning(e)
        elif e.message.startswith('Bad Request: message is not modified'):
            logging.warning(e)
        elif e.message.startswith('Bad Request: message to edit not found'):
            logging.warning(e)
        elif e.message.startswith('Bad Request: query is too old and response timeout expired or query ID is invalid'):
            logging.warning(e)
        else:
            logging.error(f'Error in bot_delayed_webhook telegram bad request: {e}')
            await notify_admins_about_error(bot, update, dp, e)
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.exception(f'Error in bot_delayed_webhook: {error_trace}')
        await notify_admins_about_error(bot, update, dp, e)


async def handle_update(update: dict):
    telegram_update = types.Update(**update)
    try:
        for i in range(config.MAX_RETRIES):
            try:
                await dp.feed_update(bot=bot, update=telegram_update)
                break
            except (
                ConnectionResetError,
                OSError,
                ClientOSError,
                ConnectionError,
                TelegramServerError,
                TelegramNetworkError,
            ) as e:
                if i == config.MAX_RETRIES - 1:
                    raise e
                continue
    except (ConnectionResetError, OSError, ClientOSError, ConnectionError, TelegramNetworkError):
        user_id = get_user_id_from_telegram_update(telegram_update)
        await handle_network_error(bot, user_id)
    except TelegramForbiddenError:
        await handle_forbidden_error(telegram_update)
    except TelegramRetryAfter as e:
        if (
            telegram_update.callback_query and
            telegram_update.callback_query.data and
            telegram_update.callback_query.data.startswith('blast_confirmation:')
        ):
            logging.warning(e)
        else:
            logging.error(f'Error in bot_webhook telegram retry after: {e}')
            asyncio.create_task(delayed_handle_update(telegram_update, e.retry_after + 30))
    except TelegramBadRequest as e:
        if e.message.startswith('Bad Request: file is too big'):
            await handle_big_file(bot, telegram_update)
        elif e.message.startswith('Bad Request: message can\'t be deleted for everyone'):
            logging.warning(e)
        elif e.message.startswith('Bad Request: message to delete not found'):
            logging.warning(e)
        elif e.message.startswith('Bad Request: message is not modified'):
            logging.warning(e)
        elif e.message.startswith('Bad Request: message to edit not found'):
            logging.warning(e)
        elif e.message.startswith('Bad Request: query is too old and response timeout expired or query ID is invalid'):
            logging.warning(e)
        else:
            error_trace = traceback.format_exc()
            logging.exception(f'Error in bot_webhook telegram bad request: {error_trace}')
            await notify_admins_about_error(bot, telegram_update, dp, e)
    except TelegramServerError as e:
        if 'Bad Gateway' in e.message:
            user_id = get_user_id_from_telegram_update(telegram_update)
            await handle_network_error(bot, user_id)
        else:
            error_trace = traceback.format_exc()
            logging.exception(f'Error in bot_webhook telegram server error: {error_trace}')
            await notify_admins_about_error(bot, telegram_update, dp, e)
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.exception(f'Error in bot_webhook: {error_trace}')
        await notify_admins_about_error(bot, telegram_update, dp, e)


@app.post(WEBHOOK_YOOKASSA_PATH)
async def yookassa_webhook(request: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(handle_yookassa_webhook, request, bot, dp)


@app.post(WEBHOOK_STRIPE_PATH)
async def stripe_webhook(request: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(handle_stripe_webhook, request, bot, dp)


@app.post(WEBHOOK_REPLICATE_PATH)
async def replicate_webhook(prediction: dict):
    is_ok = await handle_replicate_webhook(bot, dp, prediction)
    if not is_ok:
        return JSONResponse(content={}, status_code=500)


@app.post(WEBHOOK_MIDJOURNEY_PATH)
async def midjourney_webhook(body: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(handle_midjourney_webhook, bot, dp, body)


@app.post(WEBHOOK_SUNO_PATH)
async def suno_webhook(body: dict):
    is_ok = await handle_suno_webhook(bot, dp, body)
    if not is_ok:
        return JSONResponse(content={}, status_code=500)


@app.post(WEBHOOK_KLING_PATH)
async def kling_webhook(body: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(handle_kling_webhook, bot, dp, body)


@app.post(WEBHOOK_LUMA_PATH)
async def luma_webhook(body: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(handle_luma_webhook, bot, dp, body)


@app.post(WEBHOOK_PIKA_PATH)
async def pika_webhook(body: dict):
    is_ok = await handle_pika_webhook(bot, dp, body)
    if not is_ok:
        return JSONResponse(content={}, status_code=500)


@app.get('/migrate')
async def migrate_webhook(background_tasks: BackgroundTasks):
    background_tasks.add_task(migrate, bot)

    background_tasks.add_task(set_description, bot)
    background_tasks.add_task(set_commands, bot)

    return {'code': 200}


@app.get('/check-health')
async def check_health(background_tasks: BackgroundTasks):
    background_tasks.add_task(check_unresolved_requests, bot)

    return {'code': 200}


@app.get('/run-daily-tasks')
async def run_daily_tasks(background_tasks: BackgroundTasks):
    yesterday_utc_day = datetime.now(timezone.utc) - timedelta(days=1)
    await update_daily_expenses(yesterday_utc_day)

    await check_unresolved_requests(bot)
    await check_waiting_payments(bot)

    today = datetime.now()
    background_tasks.add_task(send_statistics, bot, 'day')
    if today.weekday() == 0:
        background_tasks.add_task(send_statistics, bot, 'week')
    if today.day == 1:
        background_tasks.add_task(send_statistics, bot, 'month')

    return {'code': 200}


@app.get('/update-daily-limits')
async def daily_tasks(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_daily_limits, bot, storage)

    return {'code': 200}


@app.get('/register-additional-webhooks')
async def register_additional_webhooks():
    for additional_bot, webhook_path in zip(additional_bots, WEBHOOK_ADDITIONAL_BOTS_PATHS):
        webhook_info = await additional_bot.get_webhook_info()
        webhook_url = config.WEBHOOK_URL + webhook_path
        if webhook_info.url != webhook_url:
            await additional_bot.set_webhook(url=webhook_url)


async def additional_bot_webhook(bot_instance: Bot, update: dict, background_tasks: BackgroundTasks):
    telegram_update = types.Update(**update)

    if telegram_update.message:
        chat_id = telegram_update.message.chat.id
        language_code = telegram_update.message.from_user.language_code
    elif telegram_update.edited_message:
        chat_id = telegram_update.edited_message.chat.id
        language_code = telegram_update.edited_message.from_user.language_code
    else:
        return

    bot_description = (await bot_instance.get_my_description()).description

    match = re.search(r'https?://\S+', bot_description)
    bot_link = match.group() if match else '@GPTsTurboBot'

    background_tasks.add_task(
        bot_instance.send_message,
        chat_id,
        get_localization(language_code).additional_bot_info(bot_link),
    )


for path, additional_bot in zip(WEBHOOK_ADDITIONAL_BOTS_PATHS, additional_bots):
    app.post(path)(partial(additional_bot_webhook, additional_bot))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host='0.0.0.0', port=os.getenv('PORT', 8080), timeout_keep_alive=600)
