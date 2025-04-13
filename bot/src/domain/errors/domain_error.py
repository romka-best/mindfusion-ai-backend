from bot.src.shared.error import BaseAppError


class DomainError(BaseAppError):
    pass


class QuotaExceededError(DomainError):
    pass


class RequestAlreadyStartedError(DomainError):
    pass
