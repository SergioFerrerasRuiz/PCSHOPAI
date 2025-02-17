import os
import requests
from dotenv import load_dotenv
from modules.sacaentidadesprime import procesar_con_azure

# Cargar variables de entorno
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

if not groq_api_key:
    raise ValueError("La clave API de Groq no está configurada. Define GROQ_API_KEY en el entorno.")
if not azure_api_key or not azure_endpoint:
    raise ValueError("Las credenciales de Azure OpenAI no están configuradas. Define AZURE_OPENAI_API_KEY y AZURE_OPENAI_ENDPOINT en el entorno.")

url = "https://api.groq.com/openai/v1/chat/completions"

bbddstructure = """CREATE TABLE productos (
    modelo VARCHAR(255) NOT NULL,
    procesador VARCHAR(255),
    frecuencia_cpu_ghz DECIMAL(3,1),
    ram_gb INT,
    tipo_ram VARCHAR(50),
    almacenamiento_gb INT,
    tipo_almacenamiento VARCHAR(50),
    gpu VARCHAR(255),
    pantalla_pulgadas DECIMAL(3,1),
    resolucion VARCHAR(20),
    peso_kg DECIMAL(3,1),
    precio DECIMAL(10,2),
    respuesta_ai VARCHAR(255)
);"""

def procesar_con_groq(texto):
    """Intenta procesar el texto con Groq, si falla por tamaño, llama a Azure."""
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": ""
                
            },
            {
                "role": "user",
                "content": texto
            }
        ],
        "temperature": 1
    }

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        print("texto procesado con Groq")
        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 413:
            print("Texto demasiado largo para Groq, cambiando a Azure...")
            return procesar_con_azure(texto)
        return f"Error en la API de Groq: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"Error en la API de Groq: {str(e)}"
