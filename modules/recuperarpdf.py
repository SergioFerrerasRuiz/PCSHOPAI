import json
from modules.blobstorage import descargar_archivos


def leer_json(ruta):
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            intencion = datos.get("intencion", "No disponible")
            idioma = datos.get("idioma", "No disponible")
            return intencion, idioma
    except FileNotFoundError:
        print("Error: El archivo no se encontró.")
    except json.JSONDecodeError:
        print("Error: El archivo no es un JSON válido.")
    except Exception as e:
        print(f"Error inesperado: {e}")

def obtener_pdf_desde_json(ruta_json):
    try:
        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            return datos.get("pdf", None)  # Devuelve None si no existe el campo "pdf"
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta {ruta_json}")
    except json.JSONDecodeError:
        print("Error: El archivo no contiene un JSON válido")
    return None

def recuperar_pdf():
    intnecion,idioma = leer_json("../data/json/info.json")
    pdf=obtener_pdf_desde_json("../data/json/componentesresult.json")   
    contenedor=""
    try:
        if idioma == "ruso":
            contenedor="targettranslateru"
        elif idioma == "inglés":
            contenedor="targettranslateen"
        elif idioma == "francés":
            contenedor="targettranslatefr"
        elif idioma == "chino":
            contenedor="targettranslatelzh"
        else:
            contenedor="containerseryi"

        descargar_archivos(pdf, contenedor)
    except Exception as e:
        print(f"⚠️ Error al recuperar el archivo PDF: {e}")
