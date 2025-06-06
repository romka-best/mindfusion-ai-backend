from contextlib import AsyncContextDecorator

from bot.database.models.request import RequestStatus
from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request


class RequestRecordCtx(AsyncContextDecorator):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        self.request = await write_request(*self.args, **self.kwargs)

        return self

    async def __aexit__(self, exc_type, *args):
        if exc_type is not None:
            self.request.status = RequestStatus.FINISHED

            await update_request(self.request.id, {"status": self.request.status})
