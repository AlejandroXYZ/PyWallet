import httpx
import os
import logging
from decimal import Decimal

url = os.getenv("API_DOLAR")
logger = logging.getLogger(__name__)


async def dolar_hoy():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url=url)
            respuesta = r.json()
            logger.info("Dolar Obtenido Correctamente")
            return {"status": True, "precio": respuesta["promedio"]}
        except Exception as e:
            logger.error(
                f"Ha Ocurrido un Error mientras se obtenia el precio del dólar:\n\n {e} \n\n"
            )
            return {
                "status": False,
                "mensaje": "Error, no se pudo obtener el precio del Dólar",
            }


async def convertidor(moneda: str, saldo) -> dict:
    try:
        saldo = Decimal(saldo)
        bcv = await dolar_hoy()
        dolar = Decimal(bcv["precio"])
        match moneda:
            case "VES":
                operacion = saldo / dolar
                return {
                    "status": True,
                    "saldo": f"{operacion:.2f}",
                    "moneda": "USD",
                    "anterior": "VES",
                }

            case "USD":
                operacion = saldo * dolar
                return {
                    "status": True,
                    "saldo": f"{operacion:.2f}",
                    "moneda": "VES",
                    "anterior": "USD",
                }

            case _:
                return {"status": False, "mensaje": "Tipo de Moneda no Válida"}

    except Exception as e:
        logger.error(f"Ha ocurrido un error durante la conversión:\n\n{e}\n\n")
        return {
            "status": False,
            "mensaje": "Ha Ocurrido un error durante la conversion",
        }
