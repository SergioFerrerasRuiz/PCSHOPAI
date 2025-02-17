import os
import requests
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("La clave API no está configurada. Asegúrate de definir GROQ_API_KEY en el entorno.")

# Constantes
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

def generar_mensaje_sistema(lenguaje):
    """Genera el mensaje de contexto para la IA, limitado a ordenadores y la tienda en el idioma deseado."""
    return {
        "role": "system",
        "content": (
            f"Eres un asistente virtual de una tienda especializada en la venta de ordenadores. "
            f"Solo puedes responder preguntas sobre nuestros productos (ordenadores) y sobre la tienda.\n\n"
            f"**Reglas estrictas:**\n"
            f"- Solo respondes sobre la tienda o la compra de ordenadores.\n"
            f"- Si el usuario pregunta sobre otro tema, responde: 'Lo siento, pero solo puedo brindarte información sobre nuestros ordenadores y la tienda.'\n"
            f"- Si el usuario quiere comprar un ordenador, pídele detalles **específicos** sobre los componentes que necesita.\n"
            f"- No proporciones información sobre productos que no sean ordenadores.\n\n"
            f"**Para recomendar un ordenador, necesitas que el usuario especifique estos componentes:**\n"
            f"✅ **Modelo**\n"
            f"✅ **Procesador**\n"
            f"✅ **Frecuencia de CPU (GHz)**\n"
            f"✅ **RAM (GB) y tipo de RAM**\n"
            f"✅ **Almacenamiento (GB) y tipo de almacenamiento**\n"
            f"✅ **GPU**\n"
            f"✅ **Pantalla (pulgadas) y resolución**\n"
            f"✅ **Peso (kg)**\n"
            f"✅ **Precio máximo**\n\n"
            f"**Ejemplos de respuestas adecuadas:**\n"
            f"✅ Usuario: 'Quiero comprar un ordenador.'\n"
            f"   Asistente: '¡Genial! Para recomendarte el equipo ideal, dime qué características necesitas. "
            f"Especifica el **procesador, RAM, tipo de almacenamiento, GPU, tamaño de pantalla y precio máximo**.'\n"
            f"✅ Usuario: 'Necesito una laptop para gaming.'\n"
            f"   Asistente: '¡Buena elección! Para juegos, es importante un buen procesador y una GPU potente. "
            f"Dime qué presupuesto tienes y cuántos GB de RAM y almacenamiento necesitas.'\n"
            f"✅ Usuario: '¿Me recomiendas un portátil barato?'\n"
            f"   Asistente: 'Claro, ¿qué especificaciones buscas? Necesito saber el procesador, RAM, almacenamiento y pantalla para ayudarte mejor.'\n"
            f"✅ Usuario: '¿Cuál fue el primer ordenador de la historia?'\n"
            f"   Asistente: 'Lo siento, pero solo puedo brindarte información sobre nuestros ordenadores y la tienda en {lenguaje}'\n\n"
            f"Todas las respuestas deben estar en {lenguaje}."
        )
    }

def enviar_solicitud(texto, lenguaje):
    """Envía la solicitud a la API y maneja la respuesta en el idioma solicitado."""
    if not texto.strip():
        return "No puedo responder preguntas vacías."

    payload = {
        "model": MODEL,
        "messages": [
            generar_mensaje_sistema(lenguaje),
            {"role": "user", "content": texto}
        ],
        "temperature": 1
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()

        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error en la solicitud a la API: {e}")
        return "Hubo un problema con la conexión a la API."

    except ValueError as e:
        logging.error(f"Error al procesar la respuesta de la API: {e}")
        return "La respuesta de la API no es válida."

def respuesta_asistente(texto, lenguaje):
    """Función principal que devuelve la respuesta del asistente en el idioma deseado."""
    return enviar_solicitud(texto, lenguaje)
