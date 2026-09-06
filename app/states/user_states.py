from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    waiting_query = State()


class PremiumStates(StatesGroup):
    choosing_plan = State()
    choosing_method = State()
    waiting_receipt = State()


class AIChatStates(StatesGroup):
    chatting = State()
