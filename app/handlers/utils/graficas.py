import matplotlib.pyplot as plt
from sqlalchemy import select
import seaborn as sns
import pandas as pd
import logging
import io
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Cuentas
from app.models.user import Usuarios
from app.handlers.utils.dolar import convertidor_df


logger = logging.getLogger(__name__)


async def extraer_datos(db: AsyncSession, id: int):
    try:
        logger.info("Extrayendo Datos...")
        query = await db.execute(
            select(Cuentas.nombre, Cuentas.saldo, Cuentas.moneda)
            .join(Usuarios)
            .where(Cuentas.activa == True, Usuarios.id_permitido == id)
        )
        cuentas = query.all()
        if not cuentas:
            return False
        nombres, saldos, moneda = zip(*cuentas) if cuentas else ([], [])
        datos = {"Cuenta": nombres, "Saldo": saldos, "Moneda": moneda}
        datos_convertidos = await convertidor_df(datos)
        return datos_convertidos
    except Exception as e:
        await db.rollback()
        logger.error(
            "Ha Ocurrido un error durante la creación de la gráfica de resumenes"
        )
        raise e


def saldos_actuales(datos: pd.DataFrame):
    try:
        logger.info("Generando Grafica de Resumen")
        logger.info(datos)
        df = datos
        buffer = io.BytesIO()

        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(10, 6))

        color_fondo = "#0b0c10"
        fig.patch.set_facecolor(color_fondo)
        ax.set_facecolor(color_fondo)

        colores_neon = [
            "#ff0055",
            "#00f3ff",
            "#39ff14",
            "#fdf200",
            "#b026ff",
            "#00ff9f",
        ]
        barras = sns.barplot(
            data=df,
            x="Cuenta",
            y="Saldo",
            palette=colores_neon[0 : len(df)],
            hue="Cuenta",
            legend=False,
            ax=ax,
        )

        for i, barra in enumerate(barras.patches):
            color_actual = colores_neon[i % len(colores_neon)]
            barra.set_edgecolor(color_actual)
            barra.set_linewidth(2.5)

        for contenedor in ax.containers:
            ax.bar_label(
                contenedor,
                fmt="%.2f $",
                padding=8,
                fontsize=12,
                fontweight="bold",
                color="white",
            )

        ax.set_title(
            "SALDOS ACTUALES en USD",
            fontsize=20,
            fontweight="bold",
            color="#ffffff",
            pad=20,
        )
        ax.set_ylabel(
            "Monto Disponible (USD)", fontsize=12, color="#c5c6c7", labelpad=10
        )
        ax.set_xlabel("")

        ax.grid(axis="y", color="#c5c6c7", linestyle="--", linewidth=0.5, alpha=0.15)

        sns.despine(left=True, bottom=True)
        ax.tick_params(colors="#c5c6c7", length=0)

        plt.savefig(buffer, bbox_inches="tight", dpi=300, facecolor=fig.get_facecolor())
        plt.close()
        buffer.seek(0)
        logger.info("Gráfica de Resumen Creada perfectamente")
        return buffer.read()

    except Exception as e:
        logger.error("Ha ocurrido un Error durante la creación del resumen")
        raise e
