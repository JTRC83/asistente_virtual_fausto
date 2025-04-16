import whisper

def transcribe_audio_with_pauses(audio_path, short_pause_threshold=0.5, long_pause_threshold=3.0):
    """
    Transcribe un archivo de audio usando Whisper, detectando pausas entre palabras:
      - Inserta una coma si la pausa supera short_pause_threshold.
      - Inserta un punto si supera long_pause_threshold.
    """
    # Carga el modelo base (puedes ajustar a "small", "medium", etc.)
    model = whisper.load_model("base")
    
    # Activa verbose y word_timestamps para obtener los tiempos a nivel de palabra
    result = model.transcribe(
        audio_path,
        verbose=True,
        word_timestamps=True,  # palabra por palabra
        language="es"          # ajusta a español u otro idioma si es necesario
    )

    # Si por algún motivo no se generan segmentos, devolvemos el texto sin formatear
    if not result.get("segments"):
        return result.get("text", "")
    
    transcribed_text = ""
    previous_end = 0.0  # Tiempo del final de la palabra anterior

    # Recorremos cada segmento...
    for seg in result["segments"]:
        words = seg.get("words", [])
        
        # ...y dentro de cada segmento, cada palabra
        for w in words:
            current_start = w["start"]
            # Solo se añade puntuación si no es la primera palabra
            if previous_end > 0:
                pause_duration = current_start - previous_end
                # Si la pausa es mayor que long_pause_threshold, se añade un punto
                if pause_duration > long_pause_threshold:
                    transcribed_text += ". "
                # Si es mayor que short_pause_threshold, se añade una coma
                elif pause_duration > short_pause_threshold:
                    transcribed_text += ", "
            # Añadimos la palabra, quitando espacios sobrantes
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