from bot.database.models.common import Model, Quota


def get_model_by_quota(quota: Quota) -> Model:
    quota_name = quota.replace("_", "-")

    manual_mapping = {
        "gpt4-omni": Model.CHAT_GPT,
        "gpt4-omni-mini": Model.CHAT_GPT,
        "o4-mini": Model.CHAT_GPT,
        "o3": Model.CHAT_GPT,
        "gpt4-1": Model.CHAT_GPT,
        "gpt4-1-mini": Model.CHAT_GPT,
        "claude-3-haiku": Model.CLAUDE,
        "claude-3-sonnet": Model.CLAUDE,
        "claude-3-opus": Model.CLAUDE,
        "gemini-2-flash": Model.GEMINI,
        "gemini-2-pro": Model.GEMINI,
        "gemini-1-ultra": Model.GEMINI,
        "deep-seek-v3": Model.DEEP_SEEK,
        "deep-seek-r1": Model.DEEP_SEEK,
        "stable-diffusion-xl": Model.STABLE_DIFFUSION,
        "stable-diffusion-3": Model.STABLE_DIFFUSION,
        "flux-1-dev": Model.FLUX,
        "flux-1-pro": Model.FLUX,
        "grok-2": Model.GROK,
    }

    if quota_name in manual_mapping:
        return manual_mapping[quota_name]

    model_values = {
        value
        for key, value in Model.__dict__.items()
        if not key.startswith("__") and not callable(value)
    }
    for model in model_values:
        if model in quota_name:
            return model

    raise ValueError(f"Unsupported quota: {quota}")
