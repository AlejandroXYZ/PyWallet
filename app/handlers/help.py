from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
import logging
from aiogram.types import Message

help = Router(name="help")

logger = logging.getLogger(name=__name__)


@help.message(Command("help"))
async def mostrar_ayuda(message: Message):
    mensaje = """
    🤖 <b>¡Bienvenido a PyWallet!</b>
PyWallet es una billetera digital impulsada por Inteligencia Artificial.

 <b>¿Cómo registrar transacciones?</b>
Solo escríbe lo que hiciste de forma natural y la IA hará el resto. 

<i>Ejemplos:</i>
• <code>Gasté 20$ en el supermercado usando mi cuenta BNC</code>
• <code>Me pagaron 100$ de sueldo en mi cuenta BIN</code>
• <code>Elimina la transacción 15 de mi cuenta BDV</code>

Es importante que en el mensaje siempre digas el nombre de la Cuenta abreviada 'BNC','BDV','BIN'. También el monto y la descripción

🛠 <b>Comandos Disponibles:</b>
🔹 /accounts - Menú para gestionar tus cuentas (Crear, borrar, ver saldos).
🔹 /resumen - Muestra tu dinero total y el saldo de cada cuenta.
🔹 /historial - Busca y filtra tus transacciones pasadas.
🔹 /datos - Genera gráficas de tus gastos o exporta tus datos a CSV.
🔹 /dolar - Consulta el precio oficial del dólar BCV.
🔹 /help - Muestra este menú de ayuda.

💡 <i>Tip: Para que la IA pueda registrar tus gastos, recuerda crear primero una cuenta usando el comando /accounts (usando abreviaciones de 3 a 4 letras como BNC, BDV, BIN, etc.).</i>
"""
    await message.answer(mensaje, parse_mode=ParseMode.HTML)
