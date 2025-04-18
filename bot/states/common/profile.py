from aiogram.fsm.state import State, StatesGroup


class Profile(StatesGroup):
    waiting_for_photo = State()
