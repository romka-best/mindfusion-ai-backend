from aiogram.fsm.state import State, StatesGroup


class PhotoBundleState(StatesGroup):
    wait_new_photos = State()
    wait_edit_photo = State()
