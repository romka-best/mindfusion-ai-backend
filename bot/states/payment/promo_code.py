from aiogram.fsm.state import State, StatesGroup


class PromoCode(StatesGroup):
    waiting_for_promo_code = State()
    waiting_for_promo_code_name = State()
    waiting_for_promo_code_date = State()

    waiting_for_promo_code_package_quantity = State()
    waiting_for_promo_code_discount = State()
