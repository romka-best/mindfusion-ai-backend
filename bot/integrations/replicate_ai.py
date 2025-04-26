import asyncio
import os
import base64
from typing import Optional

import replicate

from bot.config import config
from bot.database.models.common import PhotoshopAIAction, AspectRatio, StableDiffusionVersion, FluxVersion

os.environ['REPLICATE_API_TOKEN'] = config.REPLICATE_API_KEY.get_secret_value()
WEBHOOK_REPLICATE_URL = config.WEBHOOK_URL + config.WEBHOOK_REPLICATE_PATH


async def create_face_swap_images(images: list[dict]):
    tasks = [create_face_swap_image(image['target_image'], image['source_image']) for image in images]
    results = await asyncio.gather(*tasks)

    return results


async def create_face_swap_image(target_image: str, source_image: str) -> Optional[str]:
    input_parameters = {
        'input_image': target_image,
        'swap_image': source_image,
    }

    model = await replicate.models.async_get('cdingram/face-swap')
    version = await model.versions.async_get('d1d6ea8c8be89d664a07a457526f7128109dee7030fdac424788d762c71ed111')
    prediction = await replicate.predictions.async_create(
        version=version,
        input=input_parameters,
        webhook=WEBHOOK_REPLICATE_URL,
        webhook_events_filter=['completed'],
    )

    return prediction.id


async def create_flux_face_swap_image(
    prompt: str,
    main_face_image: str,
) -> Optional[str]:
    input_parameters = {
        'prompt': prompt,
        'main_face_image': main_face_image,
        'width': 1024,
        'height': 1024,
        'output_quality': 100,
    }

    model = await replicate.models.async_get('bytedance/flux-pulid')
    version = await model.versions.async_get('8baa7ef2255075b46f4d91cd238c21d31181b3e6a864463f967960bb0112525b')
    prediction = await replicate.predictions.async_create(
        version=version,
        input=input_parameters,
        webhook=WEBHOOK_REPLICATE_URL,
        webhook_events_filter=['completed'],
    )

    return prediction.id

async def create_model(owner: str, name: str, hardware: str = "cpu", visibility="private"):
    model = await replicate.models.async_create(
        owner=owner,
        name=name,
        visibility=visibility,
        hardware=hardware
    )

    return model

async def create_flux_dev_lora_trainer(
    destination: str, trigger_word: str, input_images, is_zip: bool = False
):
    if is_zip:
        data = base64.b64encode(input_images)
        data = data.decode('utf-8')
        input_images = f"data:application/zip;base64,{data}"
        del data # For GC clean up

    training_task = await replicate.trainings.async_create(
        model="ostris/flux-dev-lora-trainer",
        version="c6e78d2501e8088876e99ef21e4460d0dc121af7a4b786b9a4c2d75c620e300d",
        destination=destination,
        input={
            "steps": 3, # TODO specify steps
            "lora_rank": 16,
            "optimizer": "adamw8bit",
            "batch_size": 1,
            "resolution": "512,768,1024",
            "autocaption": True,
            "input_images": input_images,
            "trigger_word": trigger_word,
            "learning_rate": 0.0004,
            "caption_dropout_rate": 0.05,
            "cache_latents_to_disk": False,
            "gradient_checkpointing": False,
        },
    )
    del input_images # For GC clean up

    training_status = training_task.status
    training_seconds_spend = 0
    request_error_counter = 0 # if reach streak of 10 failed requests smth wrong

    await asyncio.sleep(120) # Approximately model startup
    pull_interval = 10 # TODO specify pull_interval

    while training_status not in ["succeeded", "failed", "canceled"]:
        await asyncio.sleep(pull_interval)
        training_seconds_spend += pull_interval

        try:
            training_task = await replicate.trainings.async_get(training_task.id)
            request_error_counter = 0
        except replicate.exceptions.ReplicateError:
            request_error_counter += 1

        training_status = training_task.status

        if request_error_counter == 10:
            raise Exception("training_failed", training_task)

    if training_status != "succeeded":
        raise Exception("training_failed", training_task)

    return training_task

async def create_flux_dev_lora(
    prompt, lora_weights, aspect_ratio="4:3", output_format="jpg"
) -> Optional[str]:
    model_name = "black-forest-labs/flux-dev-lora"
    input_parameters = {
        "prompt": prompt,
        "lora_weights": lora_weights,
        "aspect_ratio": aspect_ratio, # TODO choose aspect_ratio
        "output_format": output_format
    }

    prediction = await replicate.predictions.async_create(
        model=model_name,
        input=input_parameters,
        webhook=WEBHOOK_REPLICATE_URL,
        webhook_events_filter=['completed'],
    )

    return prediction.id

async def create_photoshop_ai_image(action: PhotoshopAIAction, image_url: str) -> Optional[str]:
    if action == PhotoshopAIAction.UPSCALE:
        input_parameters = {
            'img': image_url,
        }

        model = await replicate.models.async_get('tencentarc/gfpgan')
        version = await model.versions.async_get('0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c')
    elif action == PhotoshopAIAction.RESTORATION:
        input_parameters = {
            'image': image_url,
            'with_scratch': True,
        }

        model = await replicate.models.async_get('microsoft/bringing-old-photos-back-to-life')
        version = await model.versions.async_get('c75db81db6cbd809d93cc3b7e7a088a351a3349c9fa02b6d393e35e0d51ba799')
    elif action == PhotoshopAIAction.COLORIZATION:
        input_parameters = {
            'image': image_url,
        }

        model = await replicate.models.async_get('cjwbw/bigcolor')
        version = await model.versions.async_get('9451bfbf652b21a9bccc741e5c7046540faa5586cfa3aa45abc7dbb46151a4f7')
    elif action == PhotoshopAIAction.REMOVAL_BACKGROUND:
        input_parameters = {
            'image': image_url,
        }

        model = await replicate.models.async_get('cjwbw/rembg')
        version = await model.versions.async_get('fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003')
    else:
        return

    prediction = await replicate.predictions.async_create(
        version=version,
        input=input_parameters,
        webhook=WEBHOOK_REPLICATE_URL,
        webhook_events_filter=['completed'],
    )

    return prediction.id


async def create_music_gen_melody(prompt: str, duration: int) -> Optional[str]:
    input_parameters = {
        'model_version': 'stereo-melody-large',
        'output_format': 'mp3',
        'prompt': prompt,
        'duration': duration,
    }

    model = await replicate.models.async_get('meta/musicgen')
    version = await model.versions.async_get('671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb')
    prediction = await replicate.predictions.async_create(
        version=version,
        input=input_parameters,
        webhook=WEBHOOK_REPLICATE_URL,
        webhook_events_filter=['completed'],
    )

    return prediction.id


async def create_stable_diffusion_image(
    prompt: str,
    model_version: StableDiffusionVersion,
    aspect_ratio: AspectRatio,
    image_link: Optional[str] = None,
) -> Optional[str]:
    if model_version == StableDiffusionVersion.XL:
        input_parameters = {
            'prompt': prompt,
            'disable_safety_checker': True,
        }
        if image_link:
            input_parameters['image'] = image_link
            input_parameters['prompt_strength'] = 0.75

        model = await replicate.models.async_get('stability-ai/sdxl')
        version = await model.versions.async_get('7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc')

        prediction = await replicate.predictions.async_create(
            version=version,
            input=input_parameters,
            webhook=WEBHOOK_REPLICATE_URL,
            webhook_events_filter=['completed'],
        )
    elif model_version == StableDiffusionVersion.V3:
        input_parameters = {
            'prompt': prompt,
            'output_format': 'png',
            'output_quality': 100,
            'aspect_ratio': aspect_ratio,
        }
        if image_link:
            input_parameters['image'] = image_link
            input_parameters['prompt_strength'] = 0.75

        model = await replicate.models.async_get('stability-ai/stable-diffusion-3.5-large-turbo')
        prediction = await replicate.predictions.async_create(
            model=model,
            input=input_parameters,
            webhook=WEBHOOK_REPLICATE_URL,
            webhook_events_filter=['completed'],
        )
    else:
        return

    return prediction.id


async def create_flux_image(
    prompt: str,
    model_version: FluxVersion,
    aspect_ratio: AspectRatio,
    safety_tolerance=3,
    image_link: Optional[str] = None,
) -> Optional[str]:
    input_parameters = {
        'prompt': prompt,
        'aspect_ratio': aspect_ratio,
        'output_quality': 100,
    }
    version = ''
    if model_version == FluxVersion.V1_Dev:
        input_parameters.update({
            'disable_safety_checker': True,
        })
        version = 'flux-dev'
        if image_link:
            input_parameters['image'] = image_link
    elif model_version == FluxVersion.V1_Pro:
        input_parameters.update({
            'safety_tolerance': safety_tolerance,
        })
        version = 'flux-1.1-pro'
        if image_link:
            input_parameters['image_prompt'] = image_link

    model = await replicate.models.async_get(f'black-forest-labs/{version}')
    prediction = await replicate.predictions.async_create(
        model=model,
        input=input_parameters,
        webhook=WEBHOOK_REPLICATE_URL,
        webhook_events_filter=['completed'],
    )

    return prediction.id
