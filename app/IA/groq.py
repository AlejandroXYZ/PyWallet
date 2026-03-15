from groq import Groq
import logging
import os

key = os.getenv("API_KEY")

historial = [
    {
        "role": "system",
        "content": """
    Tu misión es solo analizar el input del usuario y responder solo en Json, no puedes responder más nada, solo responde en formato JSON, el usuario te dirá una transacción que hizo o que quiere hacer y tu solo debes de analizar su mensaje y responder en un JSON con esta estructura:
    {"accion": "CREATE", "monto":200.00,"etiqueta":"compra","descripcion":"compra de empanadas","cuenta":"BDV"}. Donde dice accion, solo puedes colocar estos 4 valores tal cual como están: 'CREATE','DELETE','UPDATE','READ','CONFLICT', tu deberías de saber cuál es la más adecuada dependiendo del contexto, usa conflict cuando falten datos o no se entienda el mensaje. Donde dice monto debe ser el monto de la transacción, la etiqueta debe ser solo una palabra que represente a toda la transaccion, descripción debe ser una descripción corta, y cuenta debe ser la cuenta desde que hizo la transacción abreviando su nombre en 3 o 4 letras, por ejemplo: Banco de Venezuela - BDV }
    
    Si te falta algún dato dilo pero en formato JSON siguiendo esta estructura:
    {"accion":"CONFLICT","falta":"monto,cuenta..."}.
    
    Si el mensaje es de tipo DELETE o UPDATE, responde con un JSON con esta estructura:
    {"accion":"DELETE","etiqueta":"zapato","cuenta":"BNC"}
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
