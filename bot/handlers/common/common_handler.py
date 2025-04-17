import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command, CommandStart, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, URLInputFile
from google.cloud.firestore_v1 import Increment

from bot.config import config, MessageEffect, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import (
    Quota,
    UTM,
    ChatGPTVersion,
    ClaudeGPTVersion,
    GeminiGPTVersion,
    GrokGPTVersion,
    DeepSeekVersion,
)
from bot.database.models.generation import Generation
from bot.database.models.user import UserSettings
from bot.database.operations.campaign.getters import get_campaign, get_campaign_by_name
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.user.getters import get_user, get_count_of_users_by_referral
from bot.database.operations.user.initialize_user_for_the_first_time import initialize_user_for_the_first_time
from bot.database.operations.user.updaters import update_user
from bot.handlers.ai.chat_gpt_handler import handle_chatgpt
from bot.handlers.ai.claude_handler import handle_claude
from bot.handlers.ai.deep_seek_handler import handle_deep_seek
from bot.handlers.ai.gemini_handler import handle_gemini
from bot.handlers.ai.grok_handler import handle_grok
from bot.handlers.ai.model_handler import handle_model
from bot.handlers.common.catalog_handler import handle_catalog_prompts
from bot.handlers.payment.bonus_handler import handle_bonus
from bot.handlers.payment.payment_handler import handle_subscribe, handle_package
from bot.helpers.checkers.check_user_last_activity import set_notification_stage
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.handlers.handle_model_info import handle_model_info
from bot.helpers.setters.set_commands import set_commands_for_user
from bot.helpers.updaters.update_daily_limits import update_user_daily_limits
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import (
    build_start_keyboard,
    build_start_chosen_keyboard,
    build_error_keyboard,
    build_time_limit_exceeded_chosen_keyboard,
)
from bot.keyboards.payment.bonus import build_bonus_suggestion_keyboard
from bot.locales.main import get_localization, get_user_language, set_user_language

common_router = Router()


@common_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    tasks = []
    params = message.text.split()
    user_utm = {}
    utm = [value for key, value in vars(UTM).items() if not key.startswith('__')]

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    if not user:
        default_quota = Quota.CHAT_GPT4_OMNI_MINI
        user_discount = 0
        referred_by = None
        referred_by_user = None
        if len(params) > 1:
            sub_params = params[1].split('_')
            for sub_param in sub_params:
                if '-' not in sub_param:
                    continue

                sub_param_key, sub_param_value = sub_param.split('-')
                if sub_param_key == 'r' or sub_param_key == 'referral':
                    referred_by = sub_param_value
                    referred_by_user = await get_user(referred_by)
                    referred_by_user_language_code = await get_user_language(referred_by, state.storage)

                    if referred_by_user:
                        count_of_referred_users = await get_count_of_users_by_referral(referred_by_user.id)
                        if count_of_referred_users > 40:
                            tasks.append(message.bot.send_message(
                                chat_id=referred_by_user.telegram_chat_id,
                                text=get_localization(referred_by_user_language_code).BONUS_REFERRAL_LIMIT_ERROR,
                                reply_markup=build_bonus_suggestion_keyboard(referred_by_user_language_code),
                                message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.CONGRATS),
                                disable_notification=True,
                            ))
                        else:
                            await update_user(referred_by_user.id, {
                                'balance': Increment(25),
                            })

                            tasks.append(message.bot.send_message(
                                chat_id=referred_by_user.telegram_chat_id,
                                text=get_localization(referred_by_user_language_code).BONUS_REFERRAL_SUCCESS,
                                reply_markup=build_bonus_suggestion_keyboard(referred_by_user_language_code),
                                message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.CONGRATS),
                                disable_notification=True,
                            ))
                elif sub_param_key == 'c':
                    campaign_id = sub_param_value
                    campaign = await get_campaign(campaign_id)
                    if not campaign:
                        campaign = await get_campaign_by_name(campaign_id)

                    if campaign_id == 'prompts':
                        document_path = f'campaigns/prompts.pdf'
                        document = await firebase.bucket.get_blob(document_path)
                        document_link = firebase.get_public_url(document.name)
                        tasks.append(message.bot.send_document(
                            chat_id=message.from_user.id,
                            document=URLInputFile(document_link, filename=f'prompts.pdf', timeout=300),
                            disable_notification=True,
                        ))

                    if campaign:
                        user_utm = campaign.utm
                        user_discount = campaign.discount
                elif sub_param_key == 'm' and sub_param_value in [
                    'chatgpt4omnimini',
                    'chatgpt4omni',
                    'chatgpto4mini',
                    'chatgpto3',
                    'chatgpt41mini',
                    'chatgpt41',
                    'claude3haiku',
                    'claude3sonnet',
                    'claude3opus',
                    'gemini2flash',
                    'gemini1pro',
                    'gemini1ultra',
                    'grok',
                    'deepseekv3',
                    'deepseekr1',
                    'perplexity',
                    'eightify',
                    'geminivideo',
                    'dalle',
                    'midjourney',
                    'stablediffusionxl',
                    'stablediffusion3',
                    'flux1dev',
                    'flux1pro',
                    'lumaphoton',
                    'recraft',
                    'faceswap',
                    'photoshopai',
                    'musicgen',
                    'suno',
                    'kling',
                    'runway',
                    'lumaray',
                    'pika',
                ]:
                    if sub_param_value == 'chatgpt4omnimini':
                        default_quota = Quota.CHAT_GPT4_OMNI_MINI
                    elif sub_param_value == 'chatgpt4omni':
                        default_quota = Quota.CHAT_GPT4_OMNI
                    elif sub_param_value == 'chatgpto4mini':
                        default_quota = Quota.CHAT_GPT_O_4_MINI
                    elif sub_param_value == 'chatgpto3':
                        default_quota = Quota.CHAT_GPT_O_3
                    elif sub_param_value == 'chatgpt41mini':
                        default_quota = Quota.CHAT_GPT_4_1_MINI
                    elif sub_param_value == 'chatgpt41':
                        default_quota = Quota.CHAT_GPT_4_1
                    elif sub_param_value == 'claude3haiku':
                        default_quota = Quota.CLAUDE_3_HAIKU
                    elif sub_param_value == 'claude3sonnet':
                        default_quota = Quota.CLAUDE_3_SONNET
                    elif sub_param_value == 'claude3opus':
                        default_quota = Quota.CLAUDE_3_OPUS
                    elif sub_param_value == 'gemini2flash':
                        default_quota = Quota.GEMINI_2_FLASH
                    elif sub_param_value == 'gemini2pro':
                        default_quota = Quota.GEMINI_2_PRO
                    elif sub_param_value == 'gemini1ultra':
                        default_quota = Quota.GEMINI_1_ULTRA
                    elif sub_param_value == 'grok':
                        default_quota = Quota.GROK_2
                    elif sub_param_value == 'deepseekv3':
                        default_quota = Quota.DEEP_SEEK_V3
                    elif sub_param_value == 'deepseekr1':
                        default_quota = Quota.DEEP_SEEK_R1
                    elif sub_param_value == 'perplexity':
                        default_quota = Quota.PERPLEXITY
                    elif sub_param_value == 'eightify':
                        default_quota = Quota.EIGHTIFY
                    elif sub_param_value == 'geminivideo':
                        default_quota = Quota.GEMINI_VIDEO
                    elif sub_param_value == 'dalle':
                        default_quota = Quota.DALL_E
                    elif sub_param_value == 'midjourney':
                        default_quota = Quota.MIDJOURNEY
                    elif sub_param_value == 'stablediffusionxl':
                        default_quota = Quota.STABLE_DIFFUSION_XL
                    elif sub_param_value == 'stablediffusion3':
                        default_quota = Quota.STABLE_DIFFUSION_3
                    elif sub_param_value == 'flux1dev':
                        default_quota = Quota.FLUX_1_DEV
                    elif sub_param_value == 'flux1pro':
                        default_quota = Quota.FLUX_1_PRO
                    elif sub_param_value == 'lumaphoton':
                        default_quota = Quota.LUMA_PHOTON
                    elif sub_param_value == 'recraft':
                        default_quota = Quota.RECRAFT
                    elif sub_param_value == 'faceswap':
                        default_quota = Quota.FACE_SWAP
                    elif sub_param_value == 'photoshopai':
                        default_quota = Quota.PHOTOSHOP_AI
                    elif sub_param_value == 'suno':
                        default_quota = Quota.SUNO
                    elif sub_param_value == 'musicgen':
                        default_quota = Quota.MUSIC_GEN
                    elif sub_param_value == 'kling':
                        default_quota = Quota.KLING
                    elif sub_param_value == 'runway':
                        default_quota = Quota.RUNWAY
                    elif sub_param_value == 'lumaray':
                        default_quota = Quota.LUMA_RAY
                    elif sub_param_value == 'pika':
                        default_quota = Quota.PIKA
                elif sub_param_key in utm:
                    user_utm[sub_param_key] = sub_param_value.lower()

        language_code = await set_user_language(user_id, message.from_user.language_code, state.storage)
        await set_commands_for_user(message.bot, user_id, language_code)

        chat_title = get_localization(language_code).CHAT_DEFAULT_TITLE
        transaction = firebase.db.transaction()
        user = await initialize_user_for_the_first_time(
            transaction,
            message.from_user,
            str(message.chat.id),
            chat_title,
            referred_by,
            bool(referred_by_user),
            default_quota,
            user_utm,
            user_discount,
        )
    elif user and user.is_blocked:
        user.is_blocked = False
        await update_user(user.id, {
            'is_blocked': user.is_blocked,
        })

        batch = firebase.db.batch()
        await update_user_daily_limits(message.bot, user, batch, state.storage)
        await batch.commit()
    elif user and len(params) > 1:
        sub_params = params[1].split('_')
        for sub_param in sub_params:
            if '-' not in sub_param:
                continue

            sub_param_key, sub_param_value = sub_param.split('-')
            if sub_param_key in utm:
                user_utm[sub_param_key] = sub_param_value.lower()

    user_language_code = await get_user_language(user_id, state.storage)

    await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.HELLO),
    )

    await message.answer(
        text=get_localization(user_language_code).START_INFO,
        reply_markup=build_start_keyboard(user_language_code),
        message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.CONGRATS),
    )

    await asyncio.sleep(5)

    answered_message = await message.answer(
        text=await get_switched_to_ai_model(
            user,
            get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
            user_language_code,
        ),
        reply_markup=build_switched_to_ai_keyboard(user_language_code, user.current_model),
        message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
    )

    try:
        await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
        await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
    except (TelegramBadRequest, TelegramRetryAfter):
        pass

    await handle_model_info(
        bot=message.bot,
        chat_id=user.telegram_chat_id,
        state=state,
        model=user.current_model,
        language_code=user_language_code,
    )

    if len(tasks) > 0:
        await asyncio.gather(*tasks)


@common_router.callback_query(lambda c: c.data.startswith('start:'))
async def start_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    if action == 'quick_guide':
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).START_QUICK_GUIDE_INFO,
            reply_markup=build_start_chosen_keyboard(user_language_code),
        )
    else:
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).START_INFO,
            reply_markup=build_start_keyboard(user_language_code),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.CONGRATS),
        )


@common_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    user = await get_user(str(event.from_user.id))
    user.is_blocked = True
    await update_user(user.id, {
        'is_blocked': user.is_blocked,
    })


@common_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_unblocked_bot(event: ChatMemberUpdated, state: FSMContext):
    user = await get_user(str(event.from_user.id))
    user.is_blocked = False
    await update_user(user.id, {
        'is_blocked': user.is_blocked,
    })

    batch = firebase.db.batch()
    await update_user_daily_limits(event.bot, user, batch, state.storage)
    await batch.commit()


@common_router.message(Command('help'))
async def handle_help(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    await message.answer(
        text=get_localization(user_language_code).HELP_INFO,
        reply_markup=build_error_keyboard(user_language_code),
    )


@common_router.message(Command('terms'))
async def terms(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    await message.answer(text=get_localization(user_language_code).TERMS_LINK)


@common_router.callback_query(lambda c: c.data.startswith('continue_generation:'))
async def handle_continue_generation_choose_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    action = callback_query.data.split(':')[1]

    if action == 'continue':
        await state.update_data(recognized_text=get_localization(user_language_code).MODEL_CONTINUE_GENERATING)

        if user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_Omni_Mini:
            user_quota = Quota.CHAT_GPT4_OMNI_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_Omni:
            user_quota = Quota.CHAT_GPT4_OMNI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_O_Mini:
            user_quota = Quota.CHAT_GPT_O_4_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V3_O:
            user_quota = Quota.CHAT_GPT_O_3
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_1_Mini:
            user_quota = Quota.CHAT_GPT_4_1_MINI
        elif user.settings[user.current_model][UserSettings.VERSION] == ChatGPTVersion.V4_1:
            user_quota = Quota.CHAT_GPT_4_1
        elif user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Haiku:
            user_quota = Quota.CLAUDE_3_HAIKU
        elif user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Sonnet:
            user_quota = Quota.CLAUDE_3_SONNET
        elif user.settings[user.current_model][UserSettings.VERSION] == ClaudeGPTVersion.V3_Opus:
            user_quota = Quota.CLAUDE_3_OPUS
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V2_Flash:
            user_quota = Quota.GEMINI_2_FLASH
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V2_Pro:
            user_quota = Quota.GEMINI_2_PRO
        elif user.settings[user.current_model][UserSettings.VERSION] == GeminiGPTVersion.V1_Ultra:
            user_quota = Quota.GEMINI_1_ULTRA
        elif user.settings[user.current_model][UserSettings.VERSION] == GrokGPTVersion.V2:
            user_quota = Quota.GROK_2
        elif user.settings[user.current_model][UserSettings.VERSION] == DeepSeekVersion.V3:
            user_quota = Quota.DEEP_SEEK_V3
        elif user.settings[user.current_model][UserSettings.VERSION] == DeepSeekVersion.R1:
            user_quota = Quota.DEEP_SEEK_R1
        else:
            raise NotImplementedError(
                f'AI version is not defined: {user.settings[user.current_model][UserSettings.VERSION]}'
            )

        if user_quota in [
            Quota.CHAT_GPT4_OMNI_MINI,
            Quota.CHAT_GPT4_OMNI,
            Quota.CHAT_GPT_O_4_MINI,
            Quota.CHAT_GPT_O_3,
            Quota.CHAT_GPT_4_1_MINI,
            Quota.CHAT_GPT_4_1,
        ]:
            await handle_chatgpt(callback_query.message, state, user, user_quota)
        elif user_quota in [
            Quota.CLAUDE_3_HAIKU,
            Quota.CLAUDE_3_SONNET,
            Quota.CLAUDE_3_OPUS,
        ]:
            await handle_claude(callback_query.message, state, user, user_quota)
        elif user_quota in [
            Quota.GEMINI_2_FLASH,
            Quota.GEMINI_2_PRO,
            Quota.GEMINI_1_ULTRA,
        ]:
            await handle_gemini(callback_query.message, state, user, user_quota)
        elif user_quota == Quota.GROK_2:
            await handle_grok(callback_query.message, state, user)
        elif user_quota in [
            Quota.DEEP_SEEK_V3,
            Quota.DEEP_SEEK_R1,
        ]:
            await handle_deep_seek(callback_query.message, state, user, user_quota)

        await callback_query.message.edit_reply_markup(reply_markup=None)
        await state.update_data(recognized_text=None)

    await state.clear()


@common_router.callback_query(lambda c: c.data.startswith('reaction:'))
async def reaction_selection(callback_query: CallbackQuery):
    await callback_query.answer()

    reaction, generation_id = callback_query.data.split(':')[1], callback_query.data.split(':')[2]
    await update_generation(generation_id, {
        'reaction': reaction,
    })

    if callback_query.message.caption:
        await callback_query.message.edit_reply_markup(
            reply_markup=None,
        )
    else:
        await callback_query.message.edit_caption(
            caption=Generation.get_reaction_emojis()[reaction],
            reply_markup=None,
        )


@common_router.callback_query(lambda c: c.data.startswith('buy_motivation:'))
async def buy_motivation_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]
    if action == 'open_bonus_info':
        await handle_bonus(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'open_buy_subscriptions_info':
        await handle_subscribe(callback_query.message, str(callback_query.from_user.id), state)
    elif action == 'open_buy_packages_info':
        await handle_package(callback_query.message, str(callback_query.from_user.id), state)


@common_router.callback_query(lambda c: c.data.startswith('time_limit_exceeded:'))
async def time_limit_exceeded_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    action = callback_query.data.split(':')[1]
    if action == 'remove_restriction':
        await callback_query.message.reply(
            text=get_localization(user_language_code).REMOVE_RESTRICTION_INFO,
            reply_markup=build_time_limit_exceeded_chosen_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )


@common_router.callback_query(lambda c: c.data.startswith('notify_about_quota:'))
async def notify_about_quota_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    action = callback_query.data.split(':')[1]
    if action == 'change_ai':
        await handle_model(callback_query.message, user_id, state)
    elif action == 'examples':
        await handle_catalog_prompts(
            callback_query.message,
            user_id,
            state,
            False,
        )
    elif action == 'turn_off':
        user_language_code = await get_user_language(user_id, state.storage)

        await set_notification_stage(
            user_id,
            10,
            state.storage,
        )
        await callback_query.message.reply(
            text=get_localization(user_language_code).NOTIFY_ABOUT_QUOTA_TURN_OFF_SUCCESS,
        )


@common_router.callback_query(lambda c: c.data.startswith('suggestions:'))
async def suggestions_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    action = callback_query.data.split(':')[1]
    if action == 'change_ai_model':
        await handle_model(callback_query.message, str(callback_query.from_user.id), state)


@common_router.callback_query(lambda c: c.data.endswith(':close'))
async def handle_close_selection(callback_query: CallbackQuery):
    await callback_query.answer()

    if isinstance(callback_query.message, Message):
        await callback_query.message.delete()


@common_router.callback_query(lambda c: c.data.endswith(':cancel'))
async def handle_cancel_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    if isinstance(callback_query.message, Message):
        await callback_query.message.delete()

    await state.clear()
