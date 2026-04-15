from groq import AsyncGroq
import logging
import os
import datetime

logger = logging.getLogger(name=__name__)


async def IA_Response(message: str, cuentas_usuario: list):

    logger.info("Iniciando Petición a Groq")
    fecha_actual = datetime.datetime.now()
    fecha = fecha_actual.strftime("%d/%m/%Y %H:%M")
    key = os.getenv("API_KEY")

    str_cuentas = (
        ", ".join(cuentas_usuario)
        if cuentas_usuario
        else "Ninguna cuenta registrada todavía"
    )

    prompt_sistema = f"""

    Tu misión es analizar el input del usuario y responder SOLO en formato JSON. No respondas nada más.
    
    IMPORTANTE: El usuario tiene registradas ESTAS cuentas: [{str_cuentas}].
    Si el usuario menciona una cuenta que NO está en esta lista, o si la lista está vacía, DEBES responder con:
    {{"accion": "CONFLICT", "falta": "una cuenta válida registrada (Cuentas disponibles: {str_cuentas})"}}.

    1. Estructura principal: 
    {{"accion": "CREATE","tipo":"gasto", "monto":200.00,"etiqueta":"Compras","descripcion":"compra de empanadas","cuenta":"BNC","comentario":"Espero que te hayan gustado esas empanadas", "fecha":"{fecha}"}}
    Solo usa CREATE cuando estén todos los datos necesarios. Las acciones válidas son: 'CREATE', 'DELETE', 'CONFLICT'.
    
    El monto debe ser numérico. La etiqueta debe ser una de estas: Transporte, Compras, Hogar, Ropa, Autodesarrollo, Comestibles, Entretenimiento, Recarga, Sueldo, Prestamos, Transferencia.
    El tipo debe ser: gasto, ingreso o transferencia.
    
    2. Si falta algún dato vital (monto o cuenta):
    {{"accion":"CONFLICT","falta":"monto, cuenta..."}}
    
    3. Si es un comando de borrado:
    {{"accion":"DELETE","id":1234}}
    """

    mensajes = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": message},
    ]

    if key:
        client = AsyncGroq(api_key=key)

        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes,
            temperature=0.1,
            max_tokens=300,
            stream=False,
        )
        respuesta = completion.choices[0].message.content
        logger.info(
            f"Petición Completada Correctamente\nTokens Usados: {completion.usage.total_tokens}\nTokens en el Prompt: {completion.usage.prompt_tokens}\ntokens en la respuesta: {completion.usage.completion_tokens}"
        )
        return respuesta
    else:
        logger.error("No se encontró la variable de entorno 'API_KEY'")
        raise ValueError("No se Encuentran las Variables de Entorno Necesaria")
