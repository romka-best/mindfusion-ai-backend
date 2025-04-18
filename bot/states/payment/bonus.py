from aiogram.fsm.state import State, StatesGroup


class Bonus(StatesGroup):
    waiting_for_package_quantity = State()
