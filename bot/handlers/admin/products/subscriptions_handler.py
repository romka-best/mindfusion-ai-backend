from bot.database.models.product import ProductType
from bot.database.operations.product.getters import get_products
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.admin.products.subscriptions.index import Index


class SubscriptionsHandler(BaseHandler):
    """
    Callback:
    admin:subscriptions:index
    """
    async def index(self):
        products = await get_products(is_active=True, product_type=ProductType.SUBSCRIPTION)

        await Index().send_render(self.message, products)
