import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from modules.sacaentidades import procesar_con_groq  # Método para extraer entidades
from modules.jsoner import guardar_json  # Método para guardar un diccionario como JSON
from modules.detectorintenciones import identificar_intencion  # Método para detectar intenciones
from modules.gestor import gestionar_info , leer_jsonnn# Método para gestionar la información
from modules.conversorpdf import procesar_pdf
from modules.recuperarpdf import recuperar_pdf,leer_json
from modules.formalizador import formalizacion
from modules.sacaentidades import procesar_con_azure
from modules.mongodb import buscar_datos

def vaciararchivos(ruta):
    if not os.path.exists(ruta):
        print(f"La ruta '{ruta}' no existe.")
        return
    
    if not os.path.isdir(ruta):
        print(f"La ruta '{ruta}' no es un directorio válido.")
        return
    
    for archivo in os.listdir(ruta):
        archivo_path = os.path.join(ruta, archivo)
        try:
            if os.path.isfile(archivo_path):
                os.remove(archivo_path)
                print(f"Archivo eliminado: {archivo_path}")
        except Exception as e:
            print(f"No se pudo eliminar {archivo_path}: {e}")

vaciararchivos("./data/json")


# Configuración de Flask
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, "templates"),
            static_folder=os.path.join(BASE_DIR, "static"))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

vaciararchivos(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

chat_history = []  # Historial de mensajes

@app.route('/')
def home():
    return render_template("chat.html")

@app.route('/ask', methods=['POST'])
def ask():
    vaciararchivos("./data/json")
    data = request.json
    if not data or "question" not in data:
        return jsonify({"error": "Falta la pregunta"}), 400
    
    user_question = data["question"]
    
    # Simulación de respuesta y enlace
    respuesta = procesousuario(user_question)
    enlace = recuperar_pdf()

    response_data = {"answer": respuesta}
    
    if enlace is not None:
        response_data["link"] = enlace

    return jsonify(response_data)


@app.route('/upload-file', methods=['POST'])
def upload_file():
    vaciararchivos(UPLOAD_FOLDER)
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió archivo'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Archivo vacío'}), 400

    # Verificar si el archivo tiene una extensión permitida
    extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Formato de archivo no permitido'}), 400

    # Guardar el archivo en la carpeta de subida
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Variable para el mensaje adicional
    mensaje_implementacion = "Esperando implementación... 😌"

    
    # Procesar según el tipo de archivo
    if extension == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            primeros_1000 = content[:1500]

            process=procesar_con_azure(primeros_1000)
            guardar_json(process,'data/json/componentesrequest.json')
            buscar_datos()
            identificar_intencion(primeros_1000, "./data/json/info.json")
            intencion, idioma = leer_jsonnn("./data/json/info.json")

            if idioma=="No disponible":
                idioma="español"


            result=formalizacion(idioma)

            enlace = recuperar_pdf()



        return jsonify({'message': result, 'content': result, 'additional_message': enlace}), 200
    
    elif extension == 'pdf':
        try:
            inicial = procesar_pdf(filepath)
            primeros_1000 = inicial[:1500]

            process=procesar_con_azure(primeros_1000)
            guardar_json(process,'data/json/componentesrequest.json')
            buscar_datos()
            identificar_intencion(primeros_1000, "./data/json/info.json")
            intencion, idioma = leer_jsonnn("./data/json/info.json")
            
            if idioma=="No disponible":
                idioma="español"


            result=formalizacion(idioma)

            enlace = recuperar_pdf()
            
        except Exception as e:
            return jsonify({'error': f'Error al procesar PDF: {str(e)}'}), 500
        
        return jsonify({'message': result, 'content': result, 'additional_message': enlace}), 200
    
    return jsonify({'error': 'Tipo de archivo no soportado'}), 400



def procesousuario(texto):
    identificar_intencion(texto, "./data/json/info.json")
    salida = gestionar_info(texto)
    return salida

if __name__ == "__main__":
    app.run(debug=False)
