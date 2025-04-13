from bot.src.shared.error import BaseAppError


class ApplicationError(BaseAppError):
    pass


class GenerationError(ApplicationError):
    pass
