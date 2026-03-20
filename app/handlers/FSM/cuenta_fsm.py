from aiogram.fsm.state import StatesGroup, State


class CuentaFSM(StatesGroup):
    nombre = State()
    moneda = State()
    consulta = State()
    borrar = State()
