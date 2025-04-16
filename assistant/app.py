from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import whisper
import os
import subprocess
import json
import base64

# Agregar safe globals para permitir que torch.load cargue ciertos tipos en Coqui TTS
import torch
import collections
from TTS.utils import radam

torch.serialization.add_safe_globals([collections.defaultdict, dict, radam.RAdam])

from TTS.api import TTS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # Permite CORS para pruebas

# Inicializamos el modelo de Whisper (usa "base" o el que desees)
model = whisper.load_model("base")

# Inicializamos el modelo de TTS de Coqui (en español).
tts = TTS(model_name="tts_models/es/mai/tacotron2-DDC", progress_bar=False, gpu=False)

# Variable global para saber si ya se realizó la presentación inicial
first_query = True

# Texto introductorio sobre Fausto
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
    """
    Envía el prompt (texto) en formato JSON a Gemma 3 usando ollama y pipes.
    Solo la primera vez se presenta Fausto y cuenta la anécdota; luego, responde siempre en español.
    """
    global first_query

    if first_query:
        # Instrucciones para la primera consulta
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
        # Instrucciones para las consultas posteriores
        instrucciones_siguientes = (
            "Responde siempre en español. "
            "El usuario dice: "
        )
        prompt_final = instrucciones_siguientes + prompt

    payload = json.dumps({"prompt": prompt_final})

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3"],
            input=payload,
            text=True,
            capture_output=True,
            check=True
        )
        # Devolvemos la respuesta tal cual (sin añadir "Fausto:\n")
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error en la consulta a Gemma 3: {e.stderr}"

def synthesize_text(text, output_file="response.wav"):
    """
    Usa Coqui TTS para sintetizar el texto en un archivo de audio.
    Luego codifica ese archivo en base64 y lo devuelve como cadena,
    eliminando el archivo temporal.
    """
    tts.tts_to_file(text=text, file_path=output_file)
    with open(output_file, "rb") as f:
        audio_data = f.read()
    os.remove(output_file)
    return base64.b64encode(audio_data).decode("utf-8")

@socketio.on('audio_blob')
def on_audio_blob(data):
    """
    Maneja la recepción del audio completo (tipo bytes) cuando el usuario detiene la grabación.
    Se guarda, se transcribe con Whisper, y se envía el texto a Gemma 3.
    Luego se sintetiza la respuesta con Coqui TTS y ambos resultados se emiten al cliente.
    """
    temp_filename = "temp_audio.webm"
    with open(temp_filename, "wb") as f:
        f.write(data)

    try:
        # Transcripción con Whisper
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

        # Emitimos la transcripción al cliente
        emit("transcription_partial", transcription)

        # Enviamos la transcripción a Gemma 3
        gemma_response = query_gemma(transcription)
        emit("gemma_response", gemma_response)

        # Sintetizamos la respuesta de Gemma 3 con Coqui TTS
        synthesized_audio = synthesize_text(gemma_response)
        # Emitimos el audio (en base64) para que el cliente lo reproduzca
        emit("gemma_voice", synthesized_audio)

    except Exception as e:
        emit("transcription_partial", f"Error: {str(e)}")
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@socketio.on('connect')
def on_connect():
    print("Cliente conectado.")

@socketio.on('disconnect')
def on_disconnect():
    print("Cliente desconectado.")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)