from azure.storage.blob import BlobServiceClient
import os

# Configuración
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

print(AZURE_STORAGE_CONNECTION_STRING)

if not AZURE_STORAGE_CONNECTION_STRING:
    raise ValueError("❌ ERROR: La variable de entorno 'AZURE_STORAGE_CONNECTION_STRING' no está definida.")

def obtener_url_archivo(archivo, container_name):
    try:
        # Crear cliente del servicio Blob
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(archivo)
        
        # Obtener la URL del archivo
        url_archivo = blob_client.url
        return url_archivo
    
    except Exception as e:
        return None
    