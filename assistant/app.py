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

# Fix de Coqui TTS con pickle
torch.serialization.add_safe_globals([collections.defaultdict, dict, radam.RAdam])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

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

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)