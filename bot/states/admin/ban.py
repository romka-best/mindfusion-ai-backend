from aiogram.fsm.state import State, StatesGroup


class Ban(StatesGroup):
    waiting_for_user_id = State()
