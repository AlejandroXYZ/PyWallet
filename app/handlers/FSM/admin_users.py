from aiogram.fsm.state import State, StatesGroup


class AdminUsersFSM(StatesGroup):
    telegram_id = State()
    nombre_usuario = State()
    borrar = State()
    listar = State()
