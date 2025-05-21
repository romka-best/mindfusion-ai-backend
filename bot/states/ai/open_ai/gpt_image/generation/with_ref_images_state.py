from aiogram.fsm.state import State, StatesGroup


class WithRefImagesState(StatesGroup):
    wait_ref_photos = State()
    wait_ref_text_prompt = State()
