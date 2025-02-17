import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

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

def procesar_con_azure(texto):
    client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-02-15-preview"
    )

    model = "gpt-4"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
            "role": "system",
            "content": f"""Eres un modelo de lenguaje especializado en la extracción estructurada de información sobre ordenadores portátiles y de escritorio a partir de descripciones de productos.

            Tu tarea es identificar y clasificar la información según la estructura de la siguiente base de datos SQL:

            {bbddstructure}

            ### **Reglas estrictas para la extracción:**
            1. **Solo extrae los campos definidos en la base de datos SQL.**  
            2. **Devuelve exclusivamente un JSON válido.** No añadas explicaciones, notas ni comentarios.  
            3. **Los nombres de los campos deben ser exactamente los de la base de datos SQL.**  
            4. **Si un valor no está en el texto, usa `null`. No lo infieras.**  
            5. **El JSON debe ser plano, sin objetos anidados.**  
            6. **Ejemplo de entrada y salida correcta:**"""
                        },
                        {
                            "role": "user",
                            "content": texto
                        }
        ],
        temperature= 1,
    )

    return response.choices[0].message.content