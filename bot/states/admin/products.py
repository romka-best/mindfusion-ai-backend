from aiogram.fsm.state import State, StatesGroup


class Products(StatesGroup):
    waiting_edit_new_value = State()
