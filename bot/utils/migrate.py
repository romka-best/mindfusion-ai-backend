from .migrate_gpt_image import migrate as migrate_gpt_image
from .migrate_grok import migrate as migrate_grok

async def migrate(bot):
    await migrate_gpt_image(bot)
    await migrate_grok(bot)
