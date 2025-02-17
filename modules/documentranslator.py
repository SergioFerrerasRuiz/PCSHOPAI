import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient

# Cargar variables de entorno
load_dotenv()

# Variables de configuración desde .env
key = os.getenv('AZURE_KEY')
endpoint = os.getenv('AZURE_ENDPOINT')
sourceUri = os.getenv('SOURCE_URI')
targetUri = os.getenv('TARGET_URI')
targetLanguage = 'ru'

# Crear cliente de traducción
client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

# Iniciar traducción
poller = client.begin_translation(sourceUri, targetUri, targetLanguage)
result = poller.result()

# Mostrar detalles
print('Estado:', poller.status())
print('Creado el:', poller.details.created_on)
print('Última actualización:', poller.details.last_updated_on)
print(f'Total de documentos traducidos: {poller.details.documents_total_count}')
print(f'{poller.details.documents_failed_count} fallidos')
print(f'{poller.details.documents_succeeded_count} exitosos')

# Imprimir detalles de cada documento
for document in result:
    print('Documento:', document.id)
    print('Estado:', document.status)
    if document.status == 'Succeeded':
        print('Ubicación del documento original:', document.source_document_url)
        print('Ubicación del documento traducido:', document.translated_document_url)
        print('Idioma traducido a:', document.translated_to)
    else:
        print('Error:', document.error.code, '-', document.error.message)
