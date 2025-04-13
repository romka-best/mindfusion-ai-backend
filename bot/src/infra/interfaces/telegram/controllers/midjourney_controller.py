from bot.src.application.usecases.midjourney.imagine_usecase import ImagineUsecase
from bot.database.operations.product.getters import get_product_by_quota
from bot.src.application.services.midjourney_user_quota_service import MidjourneyUserQuotaService
from bot.src.infra.gateways.firebase import GenerationGateway, RequestGateway, ReferenceImageGateway
from bot.integrations.midjourney import create_midjourney_images
from bot.locales.translate_text import translate_text
from bot.database.main import firebase
from bot.src.domain.errors.domain_error import QuotaExceededError, RequestAlreadyStartedError
from bot.src.application.errors.application_error import GenerationError
from bot.locales.main import get_user_language
from aiogram.utils.chat_action import ChatActionSender
from bot.src.infra.interfaces.telegram.presenters.midjourney.generation_presenter import GenerationPresenter
from bot.src.infra.interfaces.telegram.presenters.unknown_error_presenter import UnknownErrorPresenter
import logging


class MidjourneyController:
    def __init__(self, message, state, user, lang_code):
        self.message = message
        self.state = state
        self.user = user
        self.lang_code = lang_code

    # Hack for async initializer
    @classmethod
    async def create(cls, message, state, user):
        lang_code = await get_user_language(user.id, state.storage)
        return cls(message, state, user, lang_code)

    async def imagine(self, prompt, reference_image_filename=None):
        generation_presenter = GenerationPresenter(
            self.lang_code, self.message)
        unknown_error_presenter = UnknownErrorPresenter(
            self.lang_code, self.message)

        try:
            async with ChatActionSender.upload_photo(bot=self.message.bot, chat_id=self.message.chat.id):
                await ImagineUsecase(
                    reference_image_gateway=ReferenceImageGateway(firebase),
                    translate_text_gateway=translate_text,
                    request_gateway=RequestGateway(),
                    generation_gateway=GenerationGateway(),
                    create_midjourney_images_gateway=create_midjourney_images,
                    user_quota_service=MidjourneyUserQuotaService(self.user),
                    get_product_by_quota_gateway=get_product_by_quota,
                    prompt=prompt,
                    reference_image_filename=reference_image_filename,
                    lang_code=self.lang_code,
                    user=self.user,
                    generation_presenter=generation_presenter,
                ).execute()
        except QuotaExceededError as e:
            logging.debug(e.__class__.__name__)
            await generation_presenter.send_model_limit_exceeded(self.user.had_subscription)
        except RequestAlreadyStartedError as e:
            logging.debug(e.__class__.__name__)
            await generation_presenter.send_model_already_make_request()
        except GenerationError as e:
            logging.critical(e.__class__.__name__)
            await unknown_error_presenter.send_unknown_error_message()
        except Exception as e:
            logging.critical(e.__class__.__name__)
            await unknown_error_presenter.send_unknown_error_message()

    def upscale(self):
        pass

    def variation(self):
        pass

    def reroll(self):
        pass
