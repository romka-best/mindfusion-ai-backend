from bot.database.models.common import Model, ModelType


def get_model_type(model: Model):
    if (
        model == Model.CHAT_GPT or
        model == Model.CLAUDE or
        model == Model.GEMINI or
        model == Model.GROK or
        model == Model.DEEP_SEEK or
        model == Model.PERPLEXITY
    ):
        return ModelType.TEXT
    elif model == Model.EIGHTIFY or model == Model.GEMINI_VIDEO:
        return ModelType.SUMMARY
    elif (
        model == Model.DALL_E or
        model == Model.MIDJOURNEY or
        model == Model.STABLE_DIFFUSION or
        model == Model.FLUX or
        model == Model.LUMA_PHOTON or
        model == Model.RECRAFT or
        model == Model.FACE_SWAP or
        model == Model.PHOTOSHOP_AI
    ):
        return ModelType.IMAGE
    elif model == Model.MUSIC_GEN or model == Model.SUNO:
        return ModelType.MUSIC
    elif (
        model == Model.KLING or
        model == Model.RUNWAY or
        model == Model.LUMA_RAY or
        model == Model.PIKA
    ):
        return ModelType.VIDEO
