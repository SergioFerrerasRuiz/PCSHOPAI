import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("La clave API de Groq no está configurada. Define GROQ_API_KEY en el entorno.")

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
    precio DECIMAL(10,2)
);"""

# Historial de conversaciones
historial = []

def determinar_rol(texto):
    """Determina el rol basado en palabras clave en el texto."""
    palabras_clave_extraccion = ["características", "especificaciones", "detalles técnicos", "hardware"]
    
    if any(palabra in texto.lower() for palabra in palabras_clave_extraccion):
        return "extraccion"
    else:
        return "asistente_tienda"

def procesar_texto(texto):
    """Procesa el texto dependiendo del rol determinado y mantiene el historial."""
    rol = determinar_rol(texto)
    historial.append(f"Tú: {texto}")
    
    if rol == "extraccion":
        respuesta = procesar_con_groq(texto)
        if respuesta != "No response" and respuesta != "Error en la API de Groq: No response":
            historial.append(f"Asistente: {respuesta}")
        return respuesta
    else:
        respuesta = responder_como_asistente(texto)
        historial.append(f"Asistente: {respuesta}")
        return respuesta

def procesar_con_groq(texto):
    """Procesa el texto con Groq para la extracción de información sobre ordenadores."""
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"""Eres un modelo de lenguaje especializado en la extracción estructurada de información sobre ordenadores portátiles y de escritorio a partir de descripciones de productos.
            
            Tu tarea es identificar y clasificar la información según la estructura de la siguiente base de datos SQL:
            
            {bbddstructure}
            
            ### **Reglas estrictas para la extracción:**
            1. **Solo extrae los campos definidos en la base de datos SQL.**  
            2. **Devuelve exclusivamente un JSON válido.** No añadas explicaciones, notas ni comentarios.  
            3. **Los nombres de los campos deben ser exactamente los de la base de datos SQL.**  
            4. **Si un valor no está en el texto, usa null. No lo infieras.**  
            5. **El JSON debe ser plano, sin objetos anidados.**  
            """},
            {"role": "user", "content": texto}
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
        print("Texto procesado con Groq")
        resultado = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        
        # Si se detectan componentes, devolver solo el JSON sin nada más
        if resultado != "No response":
            return resultado
        else:
            return "No response"
    except requests.exceptions.RequestException as e:
        return f"Error en la API de Groq: {str(e)}"

def responder_como_asistente(texto):
    """Responde como asistente de tienda sin dar información de stock, catálogo o recomendaciones."""
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Eres un asistente de tienda de ordenadores. No hables sobre stock, catálogo o recomendaciones. Pide al usuario que te diga los componentes que busca."},
            {"role": "user", "content": texto}
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
        print("Texto procesado como asistente de tienda")
        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    except requests.exceptions.RequestException as e:
        return f"Error en la API de Groq: {str(e)}"

if __name__ == "__main__":
    print("Bienvenido al chatbot de asistencia de ordenadores. Escribe 'salir' para terminar.")
    while True:
        entrada = input("Tú: ")
        if entrada.lower() == "salir":
            print("¡Hasta luego!")
            break
        respuesta = procesar_texto(entrada)
        print(f"Asistente: {respuesta}")
