import asyncio
import logging

import openai
from aiogram import Router
from aiogram.enums import Currency
from aiogram.types import BufferedInputFile
from aiogram.utils.chat_action import ChatActionSender
from telegramify_markdown.mermaid import base64

from bot import keyboards
from bot.config import MessageEffect, MessageSticker, config
from bot.database.models.common import Model, Quota
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.transaction.writers import write_transaction
from bot.helpers.gpt_image.generation.pricing import Pricing
from bot.helpers.senders.send_ai_model_internal_error import send_internal_ai_model_error
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.integrations.open_ai import get_response_image
from bot.keyboards.ai.openai.gpt_image.generation.with_text_prompt import AskTextPrompt
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.states.ai.open_ai.gpt_image.generation.with_text_prompt_state import WithTextPromptState


class WithTextPromptHandler:
    async def ask_text_prompt(self, callback_query, state):
        """
        Callback:
        oai:gpt-image:gen:with_text_prompt:ask_text_prompt
        """
        user_id = str(callback_query.from_user.id)
        lang_code = await get_user_language(user_id, state.storage)

        await state.set_state(WithTextPromptState.wait_text_prompt)
        await callback_query.message.edit_text(**AskTextPrompt().render(lang_code))

    async def process_with_text(self, message, state, user):
        """
        State:
        WithTextPromptState.wait_text_prompt
        """
        try:
            await state.clear()
            lang_code = user.interface_language_code
            settings = user.settings[Model.GPT_IMAGE]
            prompt = message.text.strip()

            processing_sticker = await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
            )
            processing_message = await message.reply(
                text=get_localization(lang_code).model_image_processing_request(),
                allow_sending_without_reply=True,
            )
            try:
                async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
                    gen_result = await get_response_image(
                        version=settings["version"],
                        size=settings["size"],
                        quality=settings["quality"],
                        background=settings["background"],
                        prompt=prompt,
                        output_format="png",
                    )

                image_bytes = base64.b64decode(gen_result.data[0].b64_json)
            except openai.BadRequestError as e:
                if e.code == "content_policy_violation":
                    await message.answer_sticker(
                        sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
                    )
                    await message.reply(
                        text=get_localization(lang_code).ERROR_REQUEST_FORBIDDEN,
                        allow_sending_without_reply=True,
                    )
                    return

                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
                )

                await message.answer(
                    text=get_localization(lang_code).ERROR,
                    reply_markup=build_error_keyboard(lang_code),
                )
                await send_error_info(
                    bot=message.bot,
                    user_id=user.id,
                    info=str(e) + " " + str(settings) + f" prompt: {prompt}",
                    hashtags=[Model.GPT_IMAGE],
                )
                return
            except openai.InternalServerError:
                return await send_internal_ai_model_error(lang_code, message, Model.GPT_IMAGE)

            bg_tasks = []
            bg_tasks.append(
                asyncio.create_task(self._write_transaction_and_quota(settings, prompt, user, gen_result.usage)),
            )

            footer_text = (
                f"\n\n🖼 {user.daily_limits[Quota.GPT_IMAGE] + user.additional_usage_quota[Quota.GPT_IMAGE]}"
                if settings[UserSettings.SHOW_USAGE_QUOTA] and user.daily_limits[Quota.GPT_IMAGE] != float("inf")
                else ""
            )

            image = BufferedInputFile(image_bytes, "gen.png")
            if settings["compression"]:
                await message.reply_photo(
                    caption=f"{get_localization(lang_code).GENERATION_IMAGE_SUCCESS}{footer_text}",
                    photo=image,
                    allow_sending_without_reply=True,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.CONGRATS),
                )
            else:
                await message.reply_document(
                    caption=f"{get_localization(lang_code).GENERATION_IMAGE_SUCCESS}{footer_text}",
                    document=image,
                    allow_sending_without_reply=True,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.CONGRATS),
                )
            controls_kb = keyboards.ai.openai.gpt_image.Show().render(lang_code)
            await message.answer(get_localization(lang_code).WAITING_YOUR_NEXT_IDEA, reply_markup=controls_kb)
        except Exception as e:
            logging.exception("Unhandled")
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
            )

            await message.answer(
                text=get_localization(lang_code).ERROR,
                reply_markup=build_error_keyboard(lang_code),
            )
            await send_error_info(
                bot=message.bot,
                user_id=user.id,
                info=str(e) + " " + str(settings) + f" prompt: {prompt}",
                hashtags=[Model.GPT_IMAGE],
            )
        finally:
            await state.clear()
            await processing_message.delete()
            await processing_sticker.delete()

    async def _write_transaction_and_quota(self, settings, prompt, user, token_usage_data):
        product = await get_product_by_quota(Quota.GPT_IMAGE)
        cost = float(Pricing.get(settings[UserSettings.VERSION], token_usage_data))

        await update_user_usage_quota(user, Quota.GPT_IMAGE, quantity_to_delete=1)
        await write_transaction(
            user_id=user.id,
            type=TransactionType.EXPENSE,
            product_id=product.id,
            amount=cost,
            clear_amount=cost,
            currency=Currency.USD,
            quantity=1,
            details={
                "text": prompt,
                "has_error": False,
            },
        )


r = Router()
r.callback_query(lambda c: c.data == "oai:gpt-image:gen:with_text_prompt:ask_text_prompt")(
    WithTextPromptHandler().ask_text_prompt,
)
r.message(WithTextPromptState.wait_text_prompt)(WithTextPromptHandler().process_with_text)

with_text_prompt_router = r
