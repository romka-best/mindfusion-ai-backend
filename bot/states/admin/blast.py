from aiogram.fsm.state import State, StatesGroup


class Blast(StatesGroup):
    waiting_for_blast_letter = State()
