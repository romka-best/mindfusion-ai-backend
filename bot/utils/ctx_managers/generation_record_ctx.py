from contextlib import AsyncContextDecorator

from bot.database.models.generation import GenerationStatus
from bot.database.operations.generation.updaters import update_generation


class GenerationRecordCtx(AsyncContextDecorator):
    def __init__(self):
        self.stack = set()

    def add(self, generation):
        self.stack.add(generation)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, *args):
        if exc_type is not None:
            for generation in self.stack:
                generation.status = GenerationStatus.FINISHED
                generation.has_error = True
                await update_generation(
                    generation.id,
                    {
                        "status": generation.status,
                        "has_error": generation.has_error,
                    },
                )
                print(f"!!!!!DELETED {generation}")


