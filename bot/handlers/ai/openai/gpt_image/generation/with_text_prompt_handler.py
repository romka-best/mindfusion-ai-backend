import logging

import openai
from aiogram import Router
from aiogram.enums import Currency
from aiogram.types import BufferedInputFile
from telegramify_markdown.mermaid import base64

from bot.config import MessageSticker, config
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
from bot.keyboards.ai.openai.gpt_image.generation.with_text_prompt import Ask
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.states.ai.open_ai.gpt_image.generation.with_text_prompt_state import WithTextPromptState


class WithTextPromptHandler:
    async def ask(self, callback_query, state):
        """
        Callback:
        oai:gpt-image:gen:with_text_prompt:ask
        """
        user_id = str(callback_query.from_user.id)
        lang_code = await get_user_language(user_id, state.storage)

        await state.set_state(WithTextPromptState.wait_text_prompt)
        await callback_query.message.edit_text(**Ask().render(lang_code))

    async def process_with_text(self, message, state, user):
        """
        State:
        WithTextPromptState.wait_text_prompt
        """
        try:
            await state.clear()
            lang_code = user.language_code
            settings = user.settings[Model.GPT_IMAGE]
            prompt = message.text.strip()

            try:
                gen_response = await get_response_image(
                    version=settings["version"],
                    size=settings["size"],
                    quality=settings["quality"],
                    background=settings["background"],
                    prompt=prompt,
                    output_format="png",
                )

                image_bytes = base64.b64decode(gen_response["data"][0]["b64_json"])
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

            product = await get_product_by_quota(Quota.GPT_IMAGE)
            cost = float(Pricing[settings["size"], settings["quality"]])

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

            footer_text = (
                f"\n\n🖼 {user.daily_limits[Quota.GPT_IMAGE] + user.additional_usage_quota[Quota.GPT_IMAGE]}"
                if user.settings[UserSettings.SHOW_USAGE_QUOTA] and user.daily_limits[Quota.GPT_IMAGE] != float("inf")
                else ""
            )

            image = BufferedInputFile(image_bytes, "gen.png")
            if user.settings["compression"]:
                await message.reply_photo(
                    caption=f"{get_localization(lang_code).GENERATION_IMAGE_SUCCESS}{footer_text}",
                    photo=image,
                    allow_sending_without_reply=True,
                )
            else:
                await message.reply_document(
                    caption=f"{get_localization(lang_code).GENERATION_IMAGE_SUCCESS}{footer_text}",
                    document=image,
                    allow_sending_without_reply=True,
                )

            await update_user_usage_quota(user, Quota.GPT_IMAGE, quantity_to_delete=1)  # TODO quantity_to_delete=1?
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


r = Router()
r.callback_query(lambda c: c.data == "oai:gpt-image:gen:with_text_prompt:ask")(WithTextPromptHandler().ask)
r.message(WithTextPromptState.wait_text_prompt)(WithTextPromptHandler().process_with_text)

with_text_prompt_router = r
