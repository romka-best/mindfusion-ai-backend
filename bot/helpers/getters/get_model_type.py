from bot.database.models.common import Model, ModelType


def get_model_type(model: Model):
    if model in (
        Model.CHAT_GPT,
        Model.CLAUDE,
        Model.GEMINI,
        Model.GROK,
        Model.DEEP_SEEK,
        Model.PERPLEXITY,
        Model.GPT_IMAGE,
    ):
        return ModelType.TEXT
    if model in (Model.EIGHTIFY, Model.GEMINI_VIDEO):
        return ModelType.SUMMARY
    if model in (
        Model.DALL_E,
        Model.MIDJOURNEY,
        Model.STABLE_DIFFUSION,
        Model.FLUX,
        Model.LUMA_PHOTON,
        Model.RECRAFT,
        Model.FACE_SWAP,
        Model.PHOTOSHOP_AI,
    ):
        return ModelType.IMAGE
    if model in (Model.MUSIC_GEN, Model.SUNO):
        return ModelType.MUSIC
    if model in (Model.KLING, Model.RUNWAY, Model.LUMA_RAY, Model.PIKA):
        return ModelType.VIDEO
