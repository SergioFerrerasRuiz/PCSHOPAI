import json
from modules.sacaentidades import procesar_con_groq
from modules.shopassistant import respuesta_asistente
from modules.mongodb import buscar_datos
from modules.jsoner import guardar_json
from modules.formalizador import formalizacion
from modules.recuperarpdf import recuperar_pdf

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

def gestionar_info(texto):
    intencion, idioma = leer_json("./data/json/info.json")
    
    if intencion == "consultar_productos":
        result=procesar_con_groq(texto)
        guardar_json(result, 'data/json/componentesrequest.json')
        buscar_datos()
        recuperar_pdf
        return formalizacion(idioma) #de momento devuelvo el resultado de procesar_con_groq

    elif intencion == "error":
        intencion, idioma = leer_json("./data/json/info.json")
        return respuesta_asistente(texto,idioma)


