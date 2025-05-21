from bot.database.models.product import ProductType
from bot.database.operations.product.getters import get_products
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.admin.products.packages.index import Index


class PackagesHandler(BaseHandler):
    async def index(self):
        """
        Callback:
        admin:packages:index
        """
        products = await get_products(is_active=True, product_type=ProductType.PACKAGE)

        await Index().send_render(self.message, products)
