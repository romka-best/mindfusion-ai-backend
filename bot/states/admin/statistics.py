from aiogram.fsm.state import State, StatesGroup


class Statistics(StatesGroup):
    waiting_for_statistics_service_quantity = State()
    waiting_for_statistics_service_amount = State()
    waiting_for_statistics_service_date = State()
