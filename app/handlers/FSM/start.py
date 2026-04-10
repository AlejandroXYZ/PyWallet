from aiogram.fsm.state import State, StatesGroup


class Inicio(StatesGroup):
    iniciar = State()
    esperando_respuesta = State()
    rechazada = State()
