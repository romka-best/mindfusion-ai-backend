from bot.database.models.common import MidjourneyAction, Model, Quota
from bot.database.models.user import UserSettings
from bot.database.models.request import RequestStatus
from bot.database.models.generation import GenerationStatus
from bot.locales.types import LanguageCode
from bot.src.domain import midjourney
from bot.src.domain.errors.domain_error import QuotaExceededError, RequestAlreadyStartedError
from bot.src.application.errors.application_error import GenerationError


class ImagineUsecase:
    def __init__(
        self,
        reference_image_gateway,
        translate_text_gateway,
        request_gateway,
        generation_gateway,
        create_midjourney_images_gateway,
        user_quota_service,
        get_product_by_quota_gateway,
        generation_presenter,
        lang_code,
        prompt,
        user,
        reference_image_filename=None,
    ):
        self.action = MidjourneyAction.IMAGINE
        self.lang_code = lang_code
        self.prompt = midjourney.prompt.Parser().parse(prompt)
        self.user = user
        self.reference_image_filename = reference_image_filename
        self.processing_messages = []

        self.reference_image_gateway = reference_image_gateway
        self.translate_text_gateway = translate_text_gateway
        self.request_gateway = request_gateway
        self.generation_gateway = generation_gateway
        self.create_midjourney_images_gateway = create_midjourney_images_gateway
        self.get_product_by_quota_gateway = get_product_by_quota_gateway
        self.user_quota_service = user_quota_service
        self.generation_presenter = generation_presenter

    async def execute(self):
        self.product = await self.get_product_by_quota_gateway(Quota.MIDJOURNEY)

        await self.step_verify_user_can_generate()
        await self.step_prepare_prompt()

        try:
            await self.step_generate()
        except Exception as e:
            # Proceed only if error raised after request was saved to DB
            if hasattr(self, "request"):
                await self.step_generation_error()

            # Destroy processing msgs, because generation failed
            for msg in self.processing_messages:
                msg.delete()

            raise GenerationError from e  # We don't know why, but generation failed

    async def step_verify_user_can_generate(self):
        if not self.user_quota_service.is_quota_enough():
            raise QuotaExceededError

        user_has_unfinished_request = bool(
            await self.request_gateway.get_started_by_user_id_and_product_id(self.user.id, self.product.id)
        )
        if user_has_unfinished_request:
            raise RequestAlreadyStartedError

        return True

    async def step_prepare_prompt(self):
        # Adjust midjourney version to our supported version, currently supported versions (5.2, 6.1)
        normalized_version = midjourney.prompt.NormalizeVersion.execute(
            self.prompt.params.version,
            fallback_version=self.user.settings[Model.MIDJOURNEY][UserSettings.VERSION],
        )
        self.prompt.params.set_param("version", normalized_version)

        await self.__maybe_translate_prompt_to_english()  # if user language not english
        await self.__maybe_add_reference_image_to_prompt()  # if image passed
        self.__maybe_apply_user_settings_params_to_prompt()
        midjourney.prompt.RemoveUnsupportedParams.execute(self.prompt)

    async def step_generate(self):
        self.processing_messages = await self.generation_presenter.send_image_processing_message()

        self.request = await self.request_gateway.save(
            user_id=self.user.id,
            processing_message_ids=tuple(
                [int(msg.message_id) for msg in self.processing_messages]),
            product_id=self.product.id,
            requested=1,
            details={
                "prompt": str(self.prompt),
                "action": self.action,
                "version": self.prompt.params.version,
                "is_suggestion": False,
            },
        )

        result_id = await self.create_midjourney_images_gateway(str(self.prompt))
        await self.generation_gateway.save(
            id=result_id,
            request_id=self.request.id,
            product_id=self.product.id,
            has_error=result_id is None,
            details={
                "prompt": str(self.prompt),
                "action": self.action,
                "version": self.prompt.params.version,
                "is_suggestion": False,
            },
        )

    async def step_generation_error(self):
        self.request.status = RequestStatus.FINISHED
        await self.request_gateway.update_status(self.request.id, self.request.status)

        generations = await self.generation_gateway.get_all_by_request_id(self.request.id)
        for generation in generations:
            generation.status = GenerationStatus.FINISHED
            generation.has_error = True
            await self.generation_gateway.update(
                generation.id,
                {
                    "status": generation.status,
                    "has_error": generation.has_error,
                },
            )

    def __is_generation_with_reference_image(self):
        return self.reference_image_filename is not None

    def __maybe_apply_user_settings_params_to_prompt(self):
        """
        Fills prompt parameters from user settings if they are not provided
        Parameters provided in prompt directly have higher priority than in user settings
        """
        if self.prompt.params.version == midjourney.prompt.NullParameter:
            self.prompt.params.set_param(
                "version", self.user.settings[Model.MIDJOURNEY][UserSettings.VERSION])
        if self.prompt.params.aspect == midjourney.prompt.NullParameter:
            self.prompt.params.set_param(
                "aspect",
                self.user.settings[Model.MIDJOURNEY][UserSettings.ASPECT_RATIO],
            )

    async def __maybe_translate_prompt_to_english(self):
        if self.prompt.text != "" and self.lang_code != LanguageCode.EN:
            self.prompt.text = await self.translate_text_gateway(self.prompt.text, self.lang_code, LanguageCode.EN)

    async def __maybe_add_reference_image_to_prompt(self):
        if self.__is_generation_with_reference_image():
            image_link = await self.reference_image_gateway.get_public_link(self.user.id, self.reference_image_filename)
            self.prompt.reference_images.append(image_link)
