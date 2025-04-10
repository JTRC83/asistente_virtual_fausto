# Asistente Virtual Tipo Jarvis: Fausto

Este proyecto es un asistente virtual programado en Python que utiliza reconocimiento de voz para recibir comandos y síntesis de voz para responder, contando con una interfaz gráfica basada en Tkinter. El asistente, apodado **Fausto**, se inspira en el personaje de Goethe de la obra *Fausto* y está pensado para evolucionar hasta convertirse en un espacio interactivo donde se pueda registrar y comentar la información de los libros que ya he leído.

## Características

- **Reconocimiento de voz:** Utiliza la librería SpeechRecognition para captar los comandos hablados.
- **Síntesis de voz:** Emplea pyttsx3 para convertir texto a voz, permitiendo que el asistente responda de forma auditiva.
- **Interfaz gráfica:** Basada en Tkinter, proporciona una forma fácil e intuitiva de interactuar con el asistente.
- **Gestión de variables de entorno:** Se utiliza un archivo `.env` para configurar parámetros, integraciones y claves API.
- **Pruebas unitarias:** Se incluyen pruebas para asegurar el correcto funcionamiento de cada módulo.
- **Gestión de contenido literario:** Diseñado para ir añadiendo información de los libros leídos y posteriormente comentarlos, permitiendo mantener un registro y generar conversaciones profundas sobre la literatura, al estilo del personaje Fausto de Goethe.

## Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/JTRC83/asistente_virtual_fausto.git