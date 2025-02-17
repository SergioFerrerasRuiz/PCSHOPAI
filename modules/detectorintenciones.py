import os
import requests
from dotenv import load_dotenv
from modules.jsoner import guardar_json

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("La clave API no está configurada. Asegúrate de definir GROQ_API_KEY en el entorno.")

url = "https://api.groq.com/openai/v1/chat/completions"

def llamada_ai(texto):
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres un asistente que analiza si el usuario está consultando un producto informático. "
                    "Solo considerarás productos que encajen en la siguiente estructura de base de datos: "
                    "id, modelo, procesador, frecuencia_cpu_ghz, ram_gb, tipo_ram, almacenamiento_gb, tipo_almacenamiento, "
                    "gpu, pantalla_pulgadas, resolución, peso_kg y precio. "
                    "Si el usuario menciona que quiere comprar un ordenador pero no especifica ninguna de estas características, "
                    "la intención también debe ser 'error'. "
                    "Si el producto encaja en esta estructura, devuelve un JSON con 'intencion' como 'consultar_productos' y 'idioma'. "
                    "Si no es un producto informático o el mensaje no tiene algún componente de la estructura anterior, devuelve un JSON con 'intencion' como 'error' y 'idioma'. "
                    "Los idiomas permitidos son: 'español', 'ruso', 'inglés', 'chino' y 'francés'. "
                    "Si el usuario no menciona un idioma específico, asume que es ingles "
                    "Devuelve únicamente un JSON sin explicaciones adicionales ni texto fuera del formato JSON."
                )
            },
            {
                "role": "user",
                "content": texto
            }
        ],
        "temperature": 0
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 413:
            print("Texto demasiado largo para Groq, cambiando a Azure...")
            return procesar_con_azure(texto)
        return "{}"
    
    except requests.exceptions.RequestException as e:
        return "{}"


def identificar_intencion(texto, ruta):
    resultado = llamada_ai(texto)
    guardar_json(resultado, ruta)
    return resultado
