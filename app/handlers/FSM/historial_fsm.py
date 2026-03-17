from aiogram.fsm.state import StatesGroup, State


class HistorialFSM(StatesGroup):
    cuenta = State()
    cantidad = State()
    fecha = State()
