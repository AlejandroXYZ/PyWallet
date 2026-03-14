from groq import Groq
import os

key = os.getenv("API_KEY")

historial = [
    {
        "role": "system",
        "content": """
    Tu misión es solo analizar el input del usuario y responder solo en Json, no puedes responder más nada, solo responde en formato JSON, el usuario te dirá una transacción que hizo o que quiere hacer y tu solo debes de analizar su mensaje y responder en un JSON con esta estructura:
    {"accion": "CREATE", "monto":200.00,"etiqueta":"compra","descripcion":"compra de empanadas","cuenta":"BDV"}. Donde dice accion, solo puedes colocar estos 4 valores tal cual como están: 'CREATE','DELETE','UPDATE','READ','CONFLICT', tu deberías de saber cuál es la más adecuada dependiendo del contexto, usa conflict cuando falten datos o no se entienda el mensaje. Donde dice monto debe ser el monto de la transacción, la etiqueta debe ser solo una palabra que represente a toda la transaccion, descripción debe ser una descripción corta, y cuenta debe ser la cuenta desde que hizo la transacción abreviando su nombre en 3 o 4 letras, por ejemplo: Banco de Venezuela - BDV }
    Si te falta algún dato dilo pero en formato JSON, por ejemplo:
    {"falta":"monto,cuenta"}
    """,
    }
]


def IA_Response(message: str):

    global historial
    if len(historial) > 10:
        historial = [historial[0]] + historial[-8:]

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

        return respuesta
    else:
        raise ValueError("No se Encuentran las Variables de Entorno Necesaria")


if __name__ == "__main__":
    peticion = IA_Response(
        "Hoy compré 3 empanadas en una oferta de 3 empanadas por 1$, lo compré con mi cuenta del banco nacional de crédito"
    )
    print(peticion)
