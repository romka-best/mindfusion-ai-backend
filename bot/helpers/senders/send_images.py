import asyncio
import logging
import traceback
import uuid

from aiogram import Bot
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import InputMediaPhoto, URLInputFile
from aiohttp import ClientOSError
from redis.exceptions import ConnectionError

from bot.database.operations.user.updaters import update_user
from bot.helpers.senders.send_error_info import send_error_info


async def delayed_send_image(
    bot: Bot,
    chat_id: str,
    image: str,
    timeout: int,
    reply_markup=None,
    caption=None,
    reply_to_message_id=None,
):
    await asyncio.sleep(timeout)

    try:
        extension = image.rsplit(".", 1)[-1]
        await bot.send_photo(
            chat_id=chat_id,
            photo=URLInputFile(
                image, filename=f"{uuid.uuid4()}.{extension}", timeout=300
            ),
            reply_markup=reply_markup,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_image(
                bot,
                chat_id,
                image,
                e.retry_after + 30,
                reply_markup,
                caption,
                reply_to_message_id,
            )
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        asyncio.create_task(
            delayed_send_image(
                bot, chat_id, image, 60, reply_markup, caption, reply_to_message_id
            )
        )
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in delayed_send_image: {error_trace}")


async def send_image(
    bot: Bot,
    chat_id: str,
    image: str,
    reply_markup=None,
    caption=None,
    reply_to_message_id=None,
):
    try:
        extension = image.rsplit(".", 1)[-1]
        await bot.send_photo(
            chat_id=chat_id,
            photo=URLInputFile(
                image, filename=f"{uuid.uuid4()}.{extension}", timeout=300
            ),
            reply_markup=reply_markup,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_image(
                bot,
                chat_id,
                image,
                e.retry_after + 30,
                reply_markup,
                caption,
                reply_to_message_id,
            )
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        asyncio.create_task(
            delayed_send_image(
                bot, chat_id, image, 60, reply_markup, caption, reply_to_message_id
            )
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in send_image: {error_trace}")

        await bot.send_message(
            chat_id=chat_id,
            reply_markup=reply_markup,
            text=image,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )

        await send_error_info(
            bot=bot,
            user_id=chat_id,
            info=str(e),
            hashtags=["image"],
        )


async def delayed_send_images(
    bot: Bot,
    chat_id: str,
    images: list[str],
    timeout: int,
):
    await asyncio.sleep(timeout)

    try:
        media_group = [InputMediaPhoto(media=img) for img in images]
        await bot.send_media_group(chat_id=chat_id, media=media_group)
    except TelegramForbiddenError:
        asyncio.create_task(update_user(chat_id, {"is_blocked": True}))
    except TelegramRetryAfter as e:
        asyncio.create_task(
            delayed_send_images(bot, chat_id, images, e.retry_after + 30)
        )
    except (
        ConnectionResetError,
        OSError,
        ClientOSError,
        ConnectionError,
        TelegramNetworkError,
    ):
        asyncio.create_task(delayed_send_images(bot, chat_id, images, 60))
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f"Error in delayed_send_image: {error_trace}")


async def send_images(bot: Bot, chat_id: str, images: list[str]):
    for i in range(0, len(images), 10):
        sliced_images = images[i : i + 10]
        try:
            media_group = [InputMediaPhoto(media=img) for img in sliced_images]
            await bot.send_media_group(chat_id=chat_id, media=media_group)
        except TelegramForbiddenError:
            await update_user(
                chat_id,
                {
                    "is_blocked": True,
                },
            )
        except TelegramRetryAfter as e:
            asyncio.create_task(
                delayed_send_images(bot, chat_id, sliced_images, e.retry_after + 30)
            )
        except (
            ConnectionResetError,
            OSError,
            ClientOSError,
            ConnectionError,
            TelegramNetworkError,
        ):
            asyncio.create_task(delayed_send_images(bot, chat_id, sliced_images, 60))
        except Exception:
            error_trace = traceback.format_exc()
            logging.exception(f"Error in send_images: {error_trace}")
            for j in range(len(sliced_images)):
                try:
                    image = sliced_images[j]
                    extension = image.rsplit(".", 1)[-1]
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=URLInputFile(
                            image, filename=f"{uuid.uuid4()}.{extension}", timeout=300
                        ),
                    )
                except Exception as e:
                    error_trace = traceback.format_exc()
                    logging.exception(
                        f"Error in send_images with second try: {error_trace}"
                    )
                    await send_error_info(
                        bot=bot,
                        user_id=chat_id,
                        info=str(e),
                        hashtags=["image"],
                    )
