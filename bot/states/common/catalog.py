from aiogram.fsm.state import State, StatesGroup


class Catalog(StatesGroup):
    waiting_for_system_role_name = State()
    waiting_for_role_name = State()
    waiting_for_role_description = State()
    waiting_for_role_instruction = State()
    waiting_for_role_photo = State()

    # Admin
    waiting_for_new_role_info = State()
