#clase que extrae de un pdf que se le pase el texto que contiene

import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración con variables de entorno
ENDPOINT = os.getenv("AZURE_ENDPOINT")
KEY = os.getenv("AZURE_KEY")

# Inicializar el cliente de Azure AI
client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))

def extraer_texto(pdf_path):
    """Extrae el texto de un PDF utilizando la API de Azure AI."""
    with open(pdf_path, "rb") as pdf_file:
        poller = client.begin_analyze_document("prebuilt-read", body=pdf_file)
        result = poller.result()

    # Obtener el texto del documento usando 'line.content'
    texto_extraido = "\n".join([line.content for page in result.pages for line in page.lines])
    return texto_extraido

def procesar_pdf(pdf_path):
    """Método para procesar el PDF y manejar excepciones."""
    try:
        # Verificar si el archivo existe
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo {pdf_path} no existe.")

        # Verificar que el cliente de Azure está configurado
        if not ENDPOINT or not KEY:
            raise ValueError("Las credenciales de Azure no están configuradas correctamente.")

        # Extraer texto
        texto = extraer_texto(pdf_path)
        return texto
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

