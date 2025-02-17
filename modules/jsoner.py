import json
import os


def limpiar_json_string(json_string):
    """
    Limpia un string JSON que contiene caracteres de escape o delimitadores extra.
    """
    try:
        # Quita posibles delimitadores tipo ```json ... ```
        json_string = json_string.replace("```json", "").replace("```", "").strip()
        # Convierte el string JSON en un diccionario válido
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return None

def guardar_json(json_string, ruta):
    try:
        # Limpiar y convertir el string JSON a un diccionario
        data = limpiar_json_string(json_string)
        if data is None:
            return

        # Crear la carpeta si no existe
        directorio = os.path.dirname(ruta)
        os.makedirs(directorio, exist_ok=True)  # Crea la carpeta si no existe

        # Guardar el archivo JSON
        with open(ruta, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        print(f"✅ El archivo JSON ha sido guardado en {ruta}")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
