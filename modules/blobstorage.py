from azure.storage.blob import BlobServiceClient
import os

# Configuración
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

print(AZURE_STORAGE_CONNECTION_STRING)

if not AZURE_STORAGE_CONNECTION_STRING:
    raise ValueError("❌ ERROR: La variable de entorno 'AZURE_STORAGE_CONNECTION_STRING' no está definida.")

DESTINO = "./uploads"

def descargar_archivos(archivo, container_name):
    print("TUS MUELAS")
    try:
        print("TUS MUELAS")
        borrarantiguos()
        # Crear cliente del servicio Blob
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(container_name)

        # Crear la carpeta destino si no existe
        os.makedirs(DESTINO, exist_ok=True)

        blob_client = container_client.get_blob_client(archivo)

        # Descargar el archivo
        with open(os.path.join(DESTINO, archivo), "wb") as archivo_local:
            archivo_local.write(blob_client.download_blob().readall())

        print(f"📥 Archivo descargado: {archivo}")

    except Exception as e:
        borrarantiguos()
        print(f"⚠️ Error al descargar {archivo}: {e}")


def borrarantiguos():
    for files in os.listdir(DESTINO):
            archivo_path = os.path.join(DESTINO, files)
            try:
                if os.path.isfile(archivo_path):
                    os.remove(archivo_path)
            except Exception as e:
                return jsonify({'error': f'Error al limpiar archivos antiguos: {str(e)}'}), 500

