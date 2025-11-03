from aiogram.fsm.state import StatesGroup, State

class OrderFlow(StatesGroup):
    """Простой поток оформления: ждём количество звёзд."""
    waiting_for_quantity = State()
