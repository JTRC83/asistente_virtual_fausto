import whisper

def transcribe_audio_with_pauses(audio_path, short_pause_threshold=0.5, long_pause_threshold=3.0):
    """
    Transcribe un archivo de audio usando Whisper, detectando pausas entre palabras:
      - Inserta una coma si la pausa supera short_pause_threshold.
      - Inserta un punto si supera long_pause_threshold.
    """
    # Carga el modelo base (ajusta si quieres "small", "medium", etc.)
    model = whisper.load_model("base")
    
    # Activa verbose y word_timestamps para obtener los tiempos de cada palabra
    result = model.transcribe(
        audio_path,
        verbose=True,
        word_timestamps=True,  # palabra por palabra
        language="es"          # ajusta si quieres forzar a español u otro idioma
    )

    # Si por algún motivo no se generan segmentos, devolvemos el texto sin formatear
    if not result.get("segments"):
        return result.get("text", "")
    
    transcribed_text = ""
    
    # Variable para guardar el final de la palabra previa
    previous_end = 0.0
    
    # Recorremos cada segmento...
    for seg in result["segments"]:
        words = seg.get("words", [])
        
        # ...y dentro de cada segmento, cada palabra
        for w in words:
            current_start = w["start"]
            pause_duration = current_start - previous_end
            
            # Decidimos si insertar coma o punto en función de la pausa
            if pause_duration > long_pause_threshold:
                transcribed_text += ". "
            elif pause_duration > short_pause_threshold:
                transcribed_text += ", "
            
            # Añadimos la palabra, quitándole espacios sobrantes
            transcribed_text += w["word"].strip()
            
            # Actualizamos el end anterior con el fin de la palabra actual
            previous_end = w["end"]
    
    return transcribed_text

if __name__ == "__main__":
    # Ejemplo de uso
    audio_file = "audios/tu_archivo.mp3"
    transcription = transcribe_audio_with_pauses(audio_file)
    print("Transcripción con pausas detectadas:")
    print(transcription)