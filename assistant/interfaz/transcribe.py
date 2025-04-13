import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

if __name__ == "__main__":
    # Asegúrate de que 'tu_archivo.mp3' existe en la ruta especificada o cambia la ruta.
    audio_file = "tu_archivo.mp3"
    transcription = transcribe_audio(audio_file)
    print("Transcripción:")
    print(transcription)