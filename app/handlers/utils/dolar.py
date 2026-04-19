import httpx
import os
import logging
from decimal import Decimal
import pandas as pd
from bs4 import BeautifulSoup
import asyncio

url = os.getenv("API_DOLAR")
logger = logging.getLogger(__name__)


async def dolar_hoy():
    async with httpx.AsyncClient(verify=False) as client:
        try:
            r = await client.get(url=url)
            respuesta = r.text
            soup = BeautifulSoup(respuesta, "lxml")
            dolar = soup.select(
                selector="#dolar div.col-sm-6.col-xs-6.centrado > strong"
            )
            if not dolar:
                return {"status": False, "mensaje": "No se obtuvo el precio del dólar"}
            logger.info(f"Precio del dolar Hoy: {dolar}")
            logger.info("Dolar Obtenido Correctamente")
            dolar = Decimal(dolar[0].text.strip().replace(",", "."))
            return {"status": True, "precio": f"{dolar:.2f}"}
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


async def convertidor_df(datos: dict, tipo: str):
    try:
        logger.info("Convirtiendo VES a USD en el DataFrame")
        df = pd.DataFrame(datos)
        bcv = await dolar_hoy()
        dolar = Decimal(bcv["precio"])
        if tipo == "cuenta":
            df.loc[df["Moneda"] == "VES", "Saldo"] = df["Saldo"] / dolar
            logger.info("Convertido Correctamente")
            return df
        elif tipo == "transaccion":
            df.loc[df["moneda"] == "VES", "monto"] = df["monto"] / dolar
            logger.info("Convertido Correctamente")
            return df
    except Exception as e:
        logger.error(
            "Ha Ocurrido un Error mientras se convertian los bolívares a dolares en el DataFrame"
        )
        raise e


if __name__ == "__main__":
    print("Ejecutando...")
    url = "https://www.bcv.org.ve/"
    try:
        asyncio.run(dolar_hoy())
    except Exception as e:
        raise e
