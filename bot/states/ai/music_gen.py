from aiogram.fsm.state import State, StatesGroup


class MusicGen(StatesGroup):
    waiting_for_music_gen_duration = State()
