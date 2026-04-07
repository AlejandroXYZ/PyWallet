import traceback
from aiogram.types import ErrorEvent
import os
import html
import logging

logger = logging.getLogger(__name__)


async def error_catcher(event: ErrorEvent):
    admin = os.getenv("ADMIN_ID", None)
    error = event.exception
    detalle = traceback.format_exc()
    informe = f"<b>Error:</b>\n\n<code>{type(error).__name__}</code>\nMotivo:<code>{html.escape(str(error))}</code>\nUsuario:{event.update.message.from_user.id}\n\nTraceback:\n{html.escape(detalle[-3500:])}"

    try:
        await event.update.bot.send_message(
            chat_id=admin, text=informe, parse_mode="HTML"
        )
        if event.update.message:
            try:
                logger.error(
                    f"El usuario {event.update.message.from_user.id} le ha ocurrido un error: {Exception}"
                )
                await event.update.message.answer(
                    "Ha ocurrido un error interno, el creador ha sido notificado"
                )
            except Exception:
                pass
    except Exception:
        logger.error("Error Grave, el Catcher no pudo enviar el mensaje al admin")
