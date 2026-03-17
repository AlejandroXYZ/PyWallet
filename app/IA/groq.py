from groq import Groq
import logging
import os
import datetime

key = os.getenv("API_KEY")
fecha_actual = datetime.datetime.now()
fecha = fecha_actual.strftime("%d/%m/%Y %H:%M")

historial = [
    {
        "role": "system",
        "content": f"""
    Tu misión es solo analizar el input del usuario y responder solo en Json, no puedes responder más nada, solo responde en formato JSON, el usuario te dirá una transacción que hizo o que quiere hacer y tu solo debes de analizar su mensaje y responder en un JSON con una de estas estructuras dependiendo de lo que desee:
    1.Primera estructura: {{"accion": "CREATE","tipo":"gasto", "monto":200.00,"etiqueta":"compra","descripcion":"compra de empanadas","cuenta":"BDV","comentario":"Espero que te hayan gustado esas empanadas", "fecha"}}. Usala solo cuando estén todos los datos necesarios de lo contrario usa una de las otras dependiendo del contexto, donde dice accion, solo puedes colocar estos 3 valores tal cual como están: 'CREATE','DELETE','CONFLICT', tu deberías de saber cuál es la más adecuada dependiendo del contexto, usa conflict cuando falten datos o no se entienda el mensaje.
    Donde dice monto debe ser el monto de la transacción, la etiqueta debe ser solo una palabra que represente a toda la transaccion. 
    descripción debe ser una descripción corta, y cuenta debe ser la cuenta desde que hizo la transacción abreviando su nombre en 3 o 4 letras, por ejemplo: Banco de Venezuela - BDV 
    'tipo' debes de colocar el tipo de transaccion gasto,ingreso o transferencia, usa transferencia si es una transaccion de transferencia a cuentas propias, por ejemplo:'Transferí 40$ a mi cuenta de Binance'.
    'comentario' aquí puedes colocar un pequeño comentario de tu parte con un emoji al final, no más de 10 palabras
    'fecha', aquí debes colocar la fecha de la transaccion, la fecha de hoy es: {fecha}, si el usuario dice ayer modifica la fecha y guarda la de ayer con el mismo formato, modifica la fecha dependiendo del día que el te diga

    2. Si te falta algún dato como el monto o la cuenta dilo pero en formato JSON siguiendo esta estructura, nunca hagas una transaccion de accion de tipo"CREATE" si falta alguno de estos datos, repito NUNCA:
    {{"accion":"CONFLICT","falta":"monto,cuenta..."}}.
    
    Si el mensaje es de tipo DELETE o UPDATE, responde con un JSON con esta estructura:
    {{"accion":"DELETE","id":1234,"cuenta":"BNC"}}
    """,
    }
]

logger = logging.getLogger(name=__name__)


def IA_Response(message: str):

    logger.info("Iniciando Petición a Groq")
    global historial
    if len(historial) > 10:
        historial = [historial[0]] + historial[-8:]
        logger.info("Limpiado el historial a las 8 últimas peticiones")

    historial.append({"role": "user", "content": message})

    if key:
        client = Groq(api_key=key)

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historial,
            temperature=0.7,
            max_tokens=1024,
            stream=False,
        )
        respuesta = completion.choices[0].message.content

        historial.append({"role": "assistant", "content": respuesta})
        logger.info(
            f"Petición Completada Correctamente\nTokens Usados: {completion.usage.total_tokens}\nTokens en el Prompt: {completion.usage.prompt_tokens}\ntokens en la respuesta: {completion.usage.completion_tokens}"
        )
        return respuesta
    else:
        logger.error("No se encontró la variable de entorno 'API_KEY'")
        raise ValueError("No se Encuentran las Variables de Entorno Necesaria")
