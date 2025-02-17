import os
import requests
import logging
import json
from dotenv import load_dotenv


def leer_json(ruta):
    """Lee un archivo JSON desde la ruta proporcionada y devuelve su contenido."""
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return datos
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error al leer el archivo JSON: {e}")
        return None

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
    """Genera el mensaje de contexto para la IA, enfatizando el idioma de respuesta."""
    return {
        "role": "system",
        "content": (
            f"Eres un asistente experto en tecnología que explica las características de ordenadores "
            f"de manera clara y detallada para clientes de una tienda de informática. "
            f"Siempre debes responder en {lenguaje}. Bajo ninguna circunstancia uses otro idioma."
        )
    }



def generar_descripcion(ordenador):
    """Genera un mensaje describiendo las características del ordenador."""
    descripcion = (
        f"Hemos encontrado el ordenador en stock que mejor se adapta a tus necesidades: el {ordenador.get('modelo', 'modelo desconocido')}. "
        f"Este potente equipo está equipado con un procesador {ordenador.get('procesador', 'desconocido')} "
        f"que alcanza una frecuencia de {ordenador.get('frecuencia_cpu_ghz', 'desconocida')} GHz. Dispone de {ordenador.get('ram_gb', 'desconocida')} GB de memoria RAM {ordenador.get('tipo_ram', 'desconocida')} "
        f"y un almacenamiento de {ordenador.get('almacenamiento_gb', 'desconocido')} GB en una unidad {ordenador.get('tipo_almacenamiento', 'desconocida')}. "
        f"Para los gráficos, cuenta con una tarjeta {ordenador.get('gpu', 'desconocida')}. "
        f"Su pantalla de {ordenador.get('pantalla_pulgadas', 'desconocida')} pulgadas ofrece una resolución de {ordenador.get('resolucion', 'desconocida')}. "
        f"Pesa aproximadamente {ordenador.get('peso_kg', 'desconocido')} kg y su precio es de {ordenador.get('precio', 'desconocido')} euros."
    )
    return descripcion

def enviar_solicitud(texto, lenguaje):
    """Envía la solicitud a la API asegurando que la respuesta esté en el idioma deseado."""
    print("El lenguaje es: " + lenguaje)
    if not texto.strip():
        return "No puedo responder preguntas vacías."

    payload = {
        "model": MODEL,
        "messages": [
            generar_mensaje_sistema(lenguaje),
            {"role": "user", "content": f"Responde exclusivamente en {lenguaje}. {texto}"}
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

def formalizacion(lenguaje):
    """Lee el JSON, genera una descripción y la envía a la IA."""
    ordenador = leer_json("./data/json/componentesresult.json")
    if not ordenador:
        return "No se pudo leer el archivo JSON."
    descripcion = generar_descripcion(ordenador)
    return enviar_solicitud(descripcion,lenguaje)
