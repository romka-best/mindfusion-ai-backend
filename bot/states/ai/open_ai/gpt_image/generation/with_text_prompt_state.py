from aiogram.fsm.state import State, StatesGroup


class WithTextPromptState(StatesGroup):
    wait_text_prompt = State()

