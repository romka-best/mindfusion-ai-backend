import asyncio
import logging

from aiogram import Router
from aiogram.enums import Currency
from aiogram.types import BufferedInputFile

from bot.config import MessageSticker, config
from bot.database.models.common import Model, Quota
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.transaction.writers import write_transaction
from bot.helpers.gpt_image.generation.pricing import Pricing
from bot.helpers.senders.send_error_info import send_error_info
from bot.integrations.open_ai import create_image_edit
from bot.keyboards.ai.openai.gpt_image.generation.with_ref_images.ask import Ask
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.states.ai.open_ai.gpt_image.generation.with_ref_images_state import WithRefImagesState


class WithRefImagesHandler:
    async def ask(self, callback_query, state):
        """
        Callback: oai:gpt-image:gen:with_ref_images:ask
        """
        user_id = str(callback_query.from_user.id)
        lang_code = await get_user_language(user_id, state.storage)

        await callback_query.message.edit_text(**Ask().render(lang_code))

        await state.set_state(WithRefImagesState.wait_ref_photos)

    async def process_with_ref_photos(self, message, state, user, album):
        """
        State: WithRefImagesState.wait_ref_photos
        Message: Photo or Album
        """
        await state.set_state(WithRefImagesState.wait_ref_text_prompt)
        breakpoint()

    async def process_with_ref_text_prompt(self, message, state, user, album=None):
        """
        State: WithRefImagesState.wait_ref_text_prompt {file_ids: list[str]}
        Message: Photo or Album with filled caption
        """
        try:
            if album is None:
                album = []

            caption = next((msg.caption for msg in album), None)
            prompt = caption.strip() if caption else message.text.strip()
            settings = user.settings[Model.GPT_IMAGE]
            lang_code = user.language_code

            tg_file_ids = (
                (await state.get_data())["file_ids"] if not album else [msg.photo[-1].file_id for msg in album]
            )
            tg_files = await asyncio.gather(*[self._tg_get_file(message.bot, file_id) for file_id in tg_file_ids])
            tg_file_ios = await asyncio.gather(*[
                self._tg_get_file_io(message.bot, file.file_path) for file in tg_files
            ])

            image_bytes = (
                (
                    await create_image_edit(
                        version=settings["version"],
                        prompt=prompt,
                        image=tg_file_ios,
                        background=settings["background"],
                        quality=settings["quality"],
                        size=settings["size"],
                    )
                )
                .data[0]
                .b64_json
            )

            bg_tasks = set()
            bg_tasks.append(asyncio.create_task(self._write_transaction(settings, prompt, user.id)))

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
                )
            else:
                await message.reply_document(
                    caption=f"{get_localization(lang_code).GENERATION_IMAGE_SUCCESS}{footer_text}",
                    document=image,
                    allow_sending_without_reply=True,
                )
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
        breakpoint()

    async def _tg_get_file(self, bot, file_id):
        return await bot.get_file(file_id)

    async def _tg_get_file_io(self, bot, file_path):
        return await bot.download_file(file_path)

    async def _write_transaction(self, settings, prompt, user_id):
        product = await get_product_by_quota(Quota.GPT_IMAGE)
        cost = float(Pricing.get((settings["size"], settings["quality"])))

        await write_transaction(
            user_id=user_id,
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
r.callback_query(lambda c: c.data == "oai:gpt-image:gen:with_ref_images_ask:ask")(WithRefImagesHandler().ask)
r.message(WithRefImagesState.wait_ref_text_prompt)(WithRefImagesHandler().process_with_ref_text_prompt)
r.message(WithRefImagesState.wait_ref_photos)(WithRefImagesHandler().process_with_ref_photos)

with_text_prompt_router = r
