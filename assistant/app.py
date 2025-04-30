from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import whisper
import os
import subprocess
import json
import base64
import torch
import collections
from TTS.utils import radam
from TTS.api import TTS
from database.db_manager import guardar_conocimiento, obtener_conocimientos
from flask import request, jsonify
from database.db_manager import obtener_conocimientos
from database.db_manager import obtener_conversaciones
from database.db_manager import obtener_conocimientos
from werkzeug.utils import secure_filename
import docx
# Fix de Coqui TTS con pickle
torch.serialization.add_safe_globals([collections.defaultdict, dict, radam.RAdam])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Ruta para obtener conocimientos
@app.route("/obtener_conocimientos")
def obtener_conocimientos_api():
    conocimientos = obtener_conocimientos()
    return jsonify(conocimientos)

# Ruta para obtener conversaciones
@app.route("/obtener_conversaciones")
def obtener_conversaciones_api():
    conversaciones = obtener_conversaciones()
    return jsonify([{"fecha": fila[1], "texto": fila[2]} for fila in conversaciones])

# Ruta para obtener el estado de los temas
@app.route("/estado_temas")
def estado_temas():
    try:
        todos_los_temas = [
            "Antropología", "Arte", "Astronomía", "Biología", "Ciencia", "Ciencias Políticas",
            "Economía", "Filosofía", "Física", "Genetica", "Historia", "Inteligencia Artificial",
            "Literatura", "Matemáticas", "Música", "Psicología", "Química", "Sociología", "Tecnología"
        ]

        conocimientos = obtener_conocimientos()  # Devuelve lista de dicts con clave 'tema'
        temas_con_conocimiento = {k["tema"] for k in conocimientos}

        resultado = []
        for tema in todos_los_temas:
            estado = "ok" if tema in temas_con_conocimiento else "vacio"
            resultado.append({"tema": tema, "estado": estado})

        return jsonify(resultado)

    except Exception as e:
        print(f"[❌] Error en /estado_temas:", e)
        return jsonify([]), 500
    
# Ruta para cargar archivos
@app.route("/cargar_archivo", methods=["POST"])
def cargar_archivo():
    try:
        archivo = request.files.get("archivo")
        tema = request.form.get("tema")
        autor = request.form.get("autor")

        if not archivo or not tema or not autor:
            return jsonify({"status": "error", "msg": "Faltan campos."}), 400

        # Asegura un nombre seguro
        nombre_archivo = secure_filename(archivo.filename)
        extension = nombre_archivo.rsplit(".", 1)[-1].lower()

        if extension == "txt":
            texto = archivo.read().decode("utf-8")
        elif extension == "docx":
            doc = docx.Document(archivo)
            texto = "\n".join([p.text for p in doc.paragraphs])
        else:
            return jsonify({"status": "error", "msg": "Formato no soportado"}), 400

        from database.db_manager import guardar_conocimiento
        guardar_conocimiento(tema, autor, texto)

        print(f"📄 Archivo procesado y conocimiento guardado - Tema: {tema}, Autor: {autor}")
        return jsonify({"status": "ok"})

    except Exception as e:
        print("[❌] Error al procesar archivo:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500

# Whisper
model = whisper.load_model("base")

# TTS español
tts = TTS(model_name="tts_models/es/css10/vits", progress_bar=False, gpu=False)

first_query = True
FAUSTO_STORY = (
    "Imagina que Fausto era un hombre muy inteligente, un sabio, pero se sentía un poco triste "
    "porque pensaba que no sabía lo suficiente del mundo. Quería experimentarlo todo y conocer "
    "todos los secretos. Una anécdota famosa es la siguiente: en su búsqueda de más conocimiento "
    "y experiencias, se le aparece un personaje misterioso llamado Mefistófeles. Mefistófeles le "
    "ofrece a Fausto un trato: le mostrará todos los placeres del mundo, pero a cambio, Fausto "
    "tendrá que servirle en la otra vida. Fausto, frustrado con su vida, acepta este peligroso "
    "trato. Vive aventuras increíbles y conoce a muchas personas interesantes, pero siempre con "
    "ese pacto en la mente. Es una historia sobre la curiosidad, el deseo de aprender y las "
    "decisiones que tomamos en la vida."
)

def query_gemma(prompt):
    global first_query

    if first_query:
        instrucciones_iniciales = (
            "Responde siempre en español. "
            "Eres Fausto, un asistente virtual inspirado en el personaje de Goethe, con un sistema RAG integrado. "
            "Esta es tu historia: " + FAUSTO_STORY + "\n"
            "Preséntate brevemente y cuenta de forma anecdótica tu origen, pero solo esta vez. "
            "Luego, contesta la pregunta del usuario: "
        )
        prompt_final = instrucciones_iniciales + prompt
        first_query = False
    else:
        prompt_final = "Responde siempre en español. El usuario dice: " + prompt

    payload = json.dumps({"prompt": prompt_final})

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3"],
            input=payload,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error en la consulta a Gemma 3: {e.stderr}"

def synthesize_text(text, output_file="response.wav"):
    tts.tts_to_file(text=text, file_path=output_file)
    with open(output_file, "rb") as f:
        audio_data = f.read()
    os.remove(output_file)
    return base64.b64encode(audio_data).decode("utf-8")

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on('audio_blob')
def on_audio_blob(data):
    temp_filename = "temp_audio.webm"
    with open(temp_filename, "wb") as f:
        f.write(data)

    try:
        result = model.transcribe(
            temp_filename,
            verbose=True,
            word_timestamps=True,
            language="es"
        )
        transcription = ""
        previous_end = 0.0
        for seg in result.get("segments", []):
            for w in seg.get("words", []):
                current_start = w["start"]
                if previous_end > 0:
                    pause_duration = current_start - previous_end
                    if pause_duration > 3.0:
                        transcription += ". "
                    elif pause_duration > 0.5:
                        transcription += ", "
                transcription += w["word"].strip() + " "
                previous_end = w["end"]

        emit("transcription_partial", transcription)
        gemma_response = query_gemma(transcription)
        emit("gemma_response", gemma_response)
        synthesized_audio = synthesize_text(gemma_response)
        emit("gemma_voice", synthesized_audio)

    except Exception as e:
        emit("transcription_partial", f"Error: {str(e)}")
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@socketio.on('guardar_conocimiento')
def handle_guardar_conocimiento(data):
    try:
        tema = data.get("tema")
        autor = data.get("autor")
        texto = data.get("texto")

        guardar_conocimiento(tema, autor, texto)
        print(f"✔ Conocimiento guardado: Tema={tema}, Autor={autor}")
        emit("confirmacion_guardado", {"status": "ok"})
    except Exception as e:
        print(f"[❌] Error al guardar conocimiento:", e)
        emit("confirmacion_guardado", {"status": "error"})

@socketio.on('connect')
def on_connect():
    print("Cliente conectado.")

@socketio.on('disconnect')
def on_disconnect():
    print("Cliente desconectado.")

@socketio.on('guardar_transcripcion')
def handle_guardar_transcripcion(data):
    try:
        texto = data.get("texto")
        from database.db_manager import guardar_conversacion
        guardar_conversacion(texto)
        emit("confirmacion_transcripcion", {"status": "ok"})
    except Exception as e:
        print(f"[❌] Error al guardar transcripción:", e)
        emit("confirmacion_transcripcion", {"status": "error"})

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)