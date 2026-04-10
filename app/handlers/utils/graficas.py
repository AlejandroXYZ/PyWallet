import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as path_effects
from sqlalchemy import select
import seaborn as sns
import pandas as pd
import numpy as np
import logging
import io
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Cuentas
from app.models.user import Usuarios
from app.handlers.utils.dolar import convertidor_df
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


async def extraer_datos_resumen(db: AsyncSession, id: int):
    try:
        logger.info("Extrayendo Datos...")
        query = await db.execute(
            select(Cuentas.nombre, Cuentas.saldo, Cuentas.moneda)
            .join(Usuarios)
            .where(Cuentas.activa == True, Usuarios.id_permitido == id)
        )
        cuentas = query.all()
        if not cuentas:
            return pd.DataFrame({})
        nombres, saldos, moneda = zip(*cuentas) if cuentas else ([], [], [])
        datos = {"Cuenta": nombres, "Saldo": saldos, "Moneda": moneda}
        if "VES" in datos["Moneda"]:
            datos_convertidos = await convertidor_df(datos, "cuenta")
            return datos_convertidos
        return pd.DataFrame(datos)
    except Exception as e:
        await db.rollback()
        logger.error(
            "Ha Ocurrido un error durante la creación de la gráfica de resumenes"
        )
        raise e


async def extraer_transacciones(db: AsyncSession, id: int):
    try:
        logger.info("Extrayendo Datos de Transacciones para generar gráfica")
        query = await db.execute(
            select(
                Transaction.fecha,
                Transaction.monto,
                Cuentas.nombre,
                Cuentas.moneda,
                Transaction.etiqueta,
            )
            .join(Cuentas, Transaction.cuenta == Cuentas.id)
            .join(Usuarios, Cuentas.propietario == Usuarios.id)
            .where(
                Cuentas.activa == True,
                Usuarios.id_permitido == id,
                Transaction.tipo == "gasto",
            ),
        )
        resultados = query.all()
        fecha, monto, cuenta, moneda, etiqueta = (
            zip(*resultados) if resultados else ([], [], [], [], [])
        )
        datos = {
            "fecha": fecha,
            "monto": monto,
            "cuenta": cuenta,
            "moneda": moneda,
            "etiqueta": etiqueta,
        }
        if "VES" in datos["moneda"]:
            datos_convertidos = await convertidor_df(datos, "transaccion")
            if not datos_convertidos.empty:
                return datos_convertidos
            else:
                logger.error("Error no se obtuvieron datos")
        return pd.DataFrame(datos)
    except Exception as e:
        logger.error("Ha ocurrido un Error extrayendo las transacciones")
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


def grafico_evolucion_gastos(df: pd.DataFrame):
    if df.empty:
        logger.info("El DataFrame está vacío")
        return None

    df["fecha"] = pd.to_datetime(df["fecha"])

    dias_totales = (df["fecha"].max() - df["fecha"].min()).days

    if dias_totales <= 1:
        frecuencia = "h"
        formato_fecha = "%H:%M"
        titulo_x = "Horas del día"
    elif dias_totales <= 60:
        frecuencia = "D"
        formato_fecha = "%d %b"
        titulo_x = "Días"
    elif dias_totales <= 365:
        frecuencia = "W"
        formato_fecha = "%d %b"
        titulo_x = "Semanas"
    else:
        frecuencia = "ME"
        formato_fecha = "%b %Y"
        titulo_x = "Meses"

    df_pivot = df.pivot_table(
        index=pd.Grouper(key="fecha", freq=frecuencia),
        columns="cuenta",
        values="monto",
        aggfunc="sum",
    ).fillna(0)

    etiquetas_x = df_pivot.index.strftime(formato_fecha)
    x = np.arange(len(df_pivot))

    color_fondo = "#121212"
    color_texto = "#ffffff"
    color_cuadricula = "#2a2a2a"

    colores_neon = ["#00ffff", "#ff00ff", "#00ff00", "#ffea00", "#ff3333"]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor(color_fondo)
    ax.set_facecolor(color_fondo)

    ax.grid(True, color=color_cuadricula, linestyle="-", linewidth=0.5)

    for spine in ax.spines.values():
        spine.set_visible(False)

    for i, cuenta in enumerate(df_pivot.columns):
        y = df_pivot[cuenta].values
        color_actual = colores_neon[i % len(colores_neon)]

        ax.plot(
            x,
            y,
            "o-",
            label=cuenta,
            color=color_actual,
            linewidth=2.5,
            markersize=6,
            markerfacecolor=color_fondo,
            markeredgewidth=2,
        )

    ax.tick_params(axis="both", colors=color_texto, labelsize=9)
    ax.set_ylabel(
        "Gastos ($)", color=color_texto, fontsize=10, fontweight="bold", labelpad=10
    )
    ax.set_xlabel(
        titulo_x, color=color_texto, fontsize=10, fontweight="bold", labelpad=10
    )
    ax.set_title(
        "Evolución de Gastos por Cuenta expresado en USD",
        color=color_texto,
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    ax.set_xticks(x)
    if len(x) > 12:
        salto = len(x) // 7
        ax.set_xticks(x[::salto])
        ax.set_xticklabels(etiquetas_x[::salto], rotation=30, ha="right")
    else:
        ax.set_xticklabels(etiquetas_x, rotation=30, ha="right")

    leyenda = ax.legend(
        loc="upper left",
        bbox_to_anchor=(1, 1),
        facecolor=color_fondo,
        edgecolor=color_cuadricula,
    )
    for texto in leyenda.get_texts():
        texto.set_color(color_texto)

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(
        buffer,
        format="png",
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.1,
    )
    buffer.seek(0)
    plt.close(fig)
    logger.info("Grafica de Evolución de precios creada correctamente")
    return buffer.read()


def generar_reporte_texto(df: pd.DataFrame):
    if df.empty:
        return "No hay datos."

    df["fecha"] = pd.to_datetime(df["fecha"])
    hoy = datetime.now()
    df_mes_actual = df[
        (df["fecha"].dt.year == hoy.year) & (df["fecha"].dt.month == hoy.month)
    ].copy()

    if df_mes_actual.empty:
        return f"Sin gastos en {hoy.month}/{hoy.year}"

    df_agrupado = (
        df_mes_actual.groupby("etiqueta")["monto"].sum().sort_values(ascending=False)
    )
    total = df_agrupado.sum()

    grupos_pequeños = (df_agrupado / total * 100) < 5
    if grupos_pequeños.any():
        df_mes_actual.loc[
            df_mes_actual["etiqueta"].isin(df_agrupado[grupos_pequeños].index),
            "etiqueta",
        ] = "Otros"
        df_agrupado = (
            df_mes_actual.groupby("etiqueta")["monto"]
            .sum()
            .sort_values(ascending=False)
        )

    nombres_meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    encabezado = f"📊 <b>GASTOS DE {nombres_meses[hoy.month - 1].upper()}</b>\n\n"

    cuerpo = ""
    ancho_barra = 12

    for i, (etiqueta, monto) in enumerate(df_agrupado.items()):
        porc = (monto / total) * 100
        llenos = int((porc / 100) * ancho_barra)
        vacios = ancho_barra - llenos

        colores = ["🟩", "🟨", "🟦", "⬜️", "🟪", "🟥", "🟧", "🟫", "♥️", "♠️", "♦️", "♣️"]
        c = colores[i % len(colores)]
        barra = (c * llenos) + ("⬛" * vacios)
        cuerpo += f"{etiqueta}\n{barra} `{porc:>4.1f}%`\n\n"

    footer = f"\n💰 <b>TOTAL:</b> <b>${total:,.2f}</b>"
    return encabezado + cuerpo + footer
