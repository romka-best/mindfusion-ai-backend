from aiogram.fsm.state import State, StatesGroup


class Suno(StatesGroup):
    waiting_for_prompt = State()
    waiting_for_lyrics = State()
    waiting_for_genres = State()
