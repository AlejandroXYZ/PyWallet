import traceback
from aiogram import Bot
from aiogram.types import ErrorEvent
import os
import html
import logging

logger = logging.getLogger(__name__)


async def error_catcher(event: ErrorEvent, bot: Bot):
    admin = os.getenv("ADMIN_ID", None)
    error = event.exception
    detalle = traceback.format_exc()

    user_id = "Desconocido"

    if event.update.message:
        user_id = event.update.message.from_user.id
    elif event.update.callback_query:
        user_id = event.update.callback_query.from_user.id
    # -------------------------------------

    informe = f"<b>Error:</b>\n\n<code>{type(error).__name__}</code>\nMotivo:<code>{html.escape(str(error))}</code>\nUsuario:{user_id}\n\nTraceback:\n{html.escape(detalle[-3500:])}"

    try:
        if admin:
            await bot.send_message(chat_id=admin, text=informe, parse_mode="HTML")

        if event.update and event.update.message:
            try:
                logger.error(f"Error para usuario {user_id}: {type(error).__name__}")
                await event.update.message.answer(
                    "Ha ocurrido un error interno, el creador ha sido notificado"
                )
            except Exception:
                pass

        elif event.update.callback_query:
            try:
                await event.update.callback_query.answer(
                    "Error interno al procesar la solicitud.", show_alert=True
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Catcher falló: {e}")
