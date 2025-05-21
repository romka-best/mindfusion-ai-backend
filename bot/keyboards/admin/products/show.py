from bot.database.models.common import Currency
from bot.keyboards.base_view import BaseView
from bot.locales.types import LanguageCodeSymbols


class Show(BaseView):
    def render(self, product):
        self.plan_add([
            "edit_text",
            {
                "text": f"""
Названия:
{"\n".join([f"    {flag} {product.names.get(lang_code.lower(), '')}" for lang_code, flag in LanguageCodeSymbols._member_map_.items()])}

Описания:
{"\n".join([f"    {flag} {product.descriptions.get(lang_code.lower(), '')}" for lang_code, flag in LanguageCodeSymbols._member_map_.items()])}

Категория: {product.category}

Цены:
{"\n".join([f"    {symbol} {product.prices.get(currency_code, '')}" for currency_code, symbol in Currency.SYMBOLS.items()])}

Скидка: {product.discount}
                """,
            },
        ])

        return self.plan
