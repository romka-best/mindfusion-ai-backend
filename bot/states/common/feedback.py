from aiogram.fsm.state import State, StatesGroup


class Feedback(StatesGroup):
    waiting_for_feedback = State()
