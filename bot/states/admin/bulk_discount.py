from aiogram.fsm.state import State, StatesGroup


class BulkDiscountState(StatesGroup):
    wait_discount_value = State()
