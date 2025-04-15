from flask import Flask, render_template, request, jsonify, send_from_directory
import whisper
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de uploads (en caso de que lo necesites para el audio)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Carga del modelo Whisper
model = whisper.load_model("base")

@app.route("/")
def index():
    # Renderiza el index.html que se encuentra en la carpeta "templates"
    return render_template("index.html")

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    # Endpoint para recibir y transcribir archivos de audio usando Whisper
    if "audio" not in request.files:
        return jsonify({"error": "No se proporcionó archivo de audio"}), 400
    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    
    try:
        result = model.transcribe(filepath)
        transcription = result.get("text", "")
        os.remove(filepath)  # Elimina el archivo temporal
        return jsonify({"transcription": transcription})
    except Exception as e:
        os.remove(filepath)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ejecuta el servidor en localhost en el puerto 5000
    app.run(debug=True, port=5000)