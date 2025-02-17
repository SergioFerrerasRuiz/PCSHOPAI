import json
import os
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from bson import ObjectId
from fuzzywuzzy import fuzz

# Cargar variables de entorno
load_dotenv()

search_data_path = "./data/json/componentesrequest.json"

def json_converter(o):
    if isinstance(o, ObjectId):
        return str(o)
    raise TypeError(f"Type {o.__class__.__name__} not serializable")

def calcular_similitud(valor1, valor2):
    if valor1 and valor2:
        return fuzz.ratio(str(valor1).lower(), str(valor2).lower())
    return 0

def calcular_proximidad(valor_buscado, valor_encontrado):
    if valor_buscado is not None and valor_encontrado is not None:
        return 1 / (1 + abs(valor_buscado - valor_encontrado))
    return 0

def buscar_datos():
    uri = os.getenv("MONGO_URI")
    if uri is None:
        print("Error: No se encontró la URI en las variables de entorno.")
        return

    client = MongoClient(uri, server_api=ServerApi("1"))
    db = client["ordenadorescatalogo"]
    collection = db["catalogo"]

    try:
        with open(search_data_path, "r") as file:
            search_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: El archivo {search_data_path} no se encontró.")
        return
    except json.JSONDecodeError:
        print(f"Error: El archivo {search_data_path} no es un JSON válido.")
        return

    results = collection.find({})
    coincidencias = []
    campos_string = {"modelo", "procesador", "tipo_ram", "tipo_almacenamiento", "gpu"}
    campos_numericos = {"frecuencia_cpu_ghz", "ram_gb", "almacenamiento_gb", "pantalla_pulgadas", "peso_kg", "precio"}
    mejores_similitudes = {campo: (0, None) for campo in campos_string}

    for result in results:
        puntuacion_total = 0
        similitudes_temp = {}

        for key, value in search_data.items():
            if value is None:
                continue
            if key in result:
                if key in campos_numericos:
                    puntuacion_total += calcular_proximidad(value, result[key])
                elif key in campos_string:
                    similitud = calcular_similitud(value, result[key])
                    similitudes_temp[key] = (similitud, result)

        for campo, (similitud, registro) in similitudes_temp.items():
            if similitud > mejores_similitudes[campo][0]:
                mejores_similitudes[campo] = (similitud, registro)

        coincidencias.append((result, puntuacion_total))

    for campo, (_, mejor_registro) in mejores_similitudes.items():
        if mejor_registro:
            for i, (registro, puntuacion) in enumerate(coincidencias):
                if registro == mejor_registro:
                    coincidencias[i] = (registro, puntuacion + 1)

    if coincidencias:
        max_puntuacion = max(coincidencias, key=lambda x: x[1])[1]
        max_results = [r for r, score in coincidencias if score == max_puntuacion]
        selected_result = random.choice(max_results) if len(max_results) > 1 else max_results[0]

        with open("./data/json/componentesresult.json", "w") as f:
            json.dump(selected_result, f, default=json_converter, indent=4)

        return json.dumps(selected_result, default=json_converter, indent=4)
    else:
        print("No se encontraron coincidencias.")
        return 'No disponemos de ese componente en el catálogo'
