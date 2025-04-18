from bot.database.main import firebase
from bot.database.models.product import Product, ProductCategory, ProductType
from bot.database.operations.product.helpers import create_product_object
from bot.locales.types import LanguageCode


async def write_product(
    stripe_id: str,
    is_active: bool,
    type: ProductType,
    category: ProductCategory,
    names: dict[LanguageCode, str],
    descriptions: dict[LanguageCode, str],
    prices: dict,
    photos=None,
    order=-1,
    discount=0,
    details=None,
) -> Product:
    product = await create_product_object(
        stripe_id,
        is_active,
        type,
        category,
        names,
        descriptions,
        prices,
        photos,
        order,
        discount,
        details,
    )
    await (
        firebase.db.collection(Product.COLLECTION_NAME)
        .document(product.id)
        .set(product.to_dict())
    )

    return product
