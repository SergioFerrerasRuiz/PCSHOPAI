#CLASE QUE SIRVE PARA CONVERTIR PDF A TEXTO EN UN DIRECTORIO ESPECÍFICO

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

def convertir_pdfs_a_txt(directorio):
    """Convierte todos los archivos PDF de un directorio en archivos de texto .txt."""
    # Verificar si el directorio existe
    if not os.path.exists(directorio):
        print(f"El directorio {directorio} no existe.")
        return

    # Recorrer todos los archivos del directorio
    for archivo in os.listdir(directorio):
        # Verificar si el archivo es un PDF
        if archivo.lower().endswith(".pdf"):
            pdf_path = os.path.join(directorio, archivo)
            print(f"Procesando {archivo}...")

            # Extraer el texto del PDF
            texto_extraido = procesar_pdf(pdf_path)

            if texto_extraido:
                # Guardar el texto en un archivo .txt
                txt_path = os.path.join(directorio, archivo.replace(".pdf", ".txt"))
                with open(txt_path, "w", encoding="utf-8") as txt_file:
                    txt_file.write(texto_extraido)
                print(f"Texto extraído de {archivo} y guardado como {txt_path}")

# Llamada a la función para convertir PDFs en un directorio específico
directorio_pdfs = "../data/txt"
convertir_pdfs_a_txt(directorio_pdfs)
