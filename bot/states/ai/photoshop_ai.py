from aiogram.fsm.state import State, StatesGroup


class PhotoshopAI(StatesGroup):
    waiting_for_photo = State()
