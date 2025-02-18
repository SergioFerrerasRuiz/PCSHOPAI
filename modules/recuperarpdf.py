import json
from modules.blobstorage import obtener_url_archivo


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
    try:
        lenguaje,idioma = leer_json("./data/json/info.json") or ""  # Evita None
        if isinstance(idioma, tuple):  # Si es una tupla, tomamos el primer elemento
            idioma = idioma[0]

        if not isinstance(idioma, str):  # Si sigue sin ser string, lo convertimos
            idioma = str(idioma)

        idiomaform = idioma.strip().lower()

        contenedores = {
            "ruso": "targettranslateru",
            "inglés": "targettranslateen",
            "francés": "targettranslatefr",
            "chino": "targettranslatelzh"
        }

        contenedor = contenedores.get(idiomaform, "containerseryi")

        print(f"Contenedor seleccionado: {contenedor}")
        print(f"Idioma detectado: {repr(idioma)}")

        pdf = obtener_pdf_desde_json("./data/json/componentesresult.json")
        return obtener_url_archivo(pdf, contenedor)

    except Exception as e:
        print(f"Error en recuperar_pdf: {e}")
        return None
