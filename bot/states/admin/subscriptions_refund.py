from aiogram.fsm.state import State, StatesGroup


class SubscriptionsRefundState(StatesGroup):
    wait_user_id = State()
