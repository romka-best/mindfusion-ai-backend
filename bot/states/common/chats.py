from aiogram.fsm.state import State, StatesGroup


class Chats(StatesGroup):
    waiting_for_chat_name = State()
