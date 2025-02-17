import os
from flask import send_file
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from modules.sacaentidades import procesar_con_groq  # Método para extraer entidades
from modules.jsoner import guardar_json  # Método para guardar un diccionario como JSON
from modules.detectorintenciones import identificar_intencion  # Método para detectar intenciones
from modules.gestor import gestionar_info  # Método para gestionar la información
from modules.conversorpdf import procesar_pdf

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

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

chat_history = []  # Historial de mensajes

@app.route('/')
def home():
    return render_template("chat.html")


@app.route('/ask', methods=['POST'])
def ask():   
    vaciararchivos("./data/json")
    user_question = request.json.get('question')
    
    if not user_question:
        return jsonify({'error': 'No question provided'}), 400
    
    answer = procesousuario(user_question)
    
    # Guardar la pregunta y respuesta en el historial del chat
    chat_history.append({'user_question': user_question, 'answer': answer})

    # Llamar a send_pdf después de enviar la respuesta, para enviarlo en segundo plano
    send_pdf()

    return jsonify({'answer': answer})


@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió archivo'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Archivo vacío'}), 400

    # Verificar si el archivo tiene una extensión permitida
    extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Formato de archivo no permitido'}), 400

    # Eliminar archivos antiguos en UPLOAD_FOLDER
    for archivo in os.listdir(app.config['UPLOAD_FOLDER']):
        archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], archivo)
        try:
            if os.path.isfile(archivo_path):
                os.remove(archivo_path)
        except Exception as e:
            return jsonify({'error': f'Error al limpiar archivos antiguos: {str(e)}'}), 500

    # Guardar el nuevo archivo
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Procesar el archivo según su tipo
    if extension == 'txt':
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                answerdocument=procesousuario(content)
                print(content)

            return jsonify({'filename': filename, 'message': answerdocument}), 200
        
        except Exception as e:
            return jsonify({'error': f'Error al procesar el archivo TXT: {str(e)}'}), 500

    elif extension == 'pdf':
        textodelarchivo=procesar_pdf()
        answerdocument=procesousuario(textodelarchivo)
        # Aquí se llama a cognitiveservices para que lo pase a texto
        return jsonify({'filename': filename, 'message': answerdocument}), 200
    

    return jsonify({'error': 'Formato de archivo no reconocido'}), 400

@app.route('/send-pdf', methods=['GET'])
def send_pdf():
    pdf_folder = os.path.join(app.config['UPLOAD_FOLDER'])
    
    if not os.path.exists(pdf_folder):
        return jsonify({'error': 'La carpeta de PDFs no existe'}), 400
    
    archivos_pdf = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    if not archivos_pdf:
        return jsonify({'error': 'No hay archivos PDF en la carpeta'}), 400
    
    pdf_path = os.path.join(pdf_folder, archivos_pdf[0])  # Tomamos el primer PDF encontrado
    print(f"Buscando archivos PDF en: {pdf_path}")
    try:
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Error al enviar el archivo: {str(e)}'}), 500


def procesousuario(texto):
    identificar_intencion(texto,"./data/json/info.json")
    salida = gestionar_info(texto)
    return salida


if __name__ == "__main__":
    app.run(debug=False)
