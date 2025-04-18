from aiogram.fsm.state import State, StatesGroup


class Payment(StatesGroup):
    waiting_for_package_quantity = State()
