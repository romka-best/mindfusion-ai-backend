from bot.database.main import firebase
from bot.database.models.product import Product, ProductCategory, ProductType
from bot.locales.types import LanguageCode


async def create_product_object(
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
    product_ref = firebase.db.collection(Product.COLLECTION_NAME).document()
    return Product(
        id=product_ref.id,
        stripe_id=stripe_id,
        is_active=is_active,
        type=type,
        category=category,
        names=names,
        descriptions=descriptions,
        prices=prices,
        photos=photos,
        order=order,
        discount=discount,
        details=details,
    )
