# 🧠 Asistente Virtual FAUSTO

**FAUSTO** es un asistente virtual conversacional, con capacidad de **voz**, **memoria a largo plazo** (usando RAG con embeddings) y una interfaz gráfica para gestionar transcripciones y documentos.

---

## 🚀 Características principales

* 🎧 Transcripción de voz con [Whisper](https://github.com/openai/whisper)
* 🗣️ Respuestas habladas usando [Coqui TTS](https://github.com/coqui-ai/TTS)
* 📀 Almacenamiento de transcripciones y conocimientos en SQLite
* 🧠 Recuperación de información mediante RAG (**Retrieval-Augmented Generation**) con:

  * **Embeddings locales** usando HuggingFace y el modelo `all-MiniLM-L6-v2`
  * Similitud por `cosine similarity` con `scikit-learn`
* ✍️ Carga de archivos `.txt` y `.docx` como documentos de conocimiento
* 🧹 Integración con **Gemma 3** (vía `ollama`) para generación de respuestas
* 💡 Modal de historial y documentos con edición, eliminación y visualización por páginas

---

## 📂 Estructura del proyecto

```
asistente_virtual_fausto/
│
├── assistant/
│   ├── app.py              # Servidor principal Flask + Socket.IO
│   ├── static/             # JS, CSS, imágenes
│   ├── templates/          # index.html
│   └── database/
│       ├── db_manager.py   # Lógica SQLite
│       └── fausto.db       # Base de datos
├── venv/                   # Entorno virtual
└── README.md
```

---

## 🛠️ Requisitos

Instala los paquetes necesarios:

```bash
pip install flask flask_socketio openai-whisper coqui-tts sentence-transformers scikit-learn python-docx
```

---

## 🎯 Instrucciones de uso

1. Clona el proyecto y entra en la carpeta:

```bash
git clone https://github.com/tu_usuario/asistente_virtual_fausto.git
cd asistente_virtual_fausto
```

2. Inicia el entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala dependencias (ver sección anterior)
4. Arranca la aplicación:

```bash
python assistant/app.py
```

5. Abre en el navegador:

```
http://localhost:5000
```

---

## 🎤 Flujo de trabajo

### 1. Transcripción por voz

* El usuario habla → Whisper transcribe → se muestra en pantalla.

### 2. Generación de respuesta

* Se busca contexto usando embeddings (MiniLM) y cosine\_similarity.
* Se envía a Gemma 3 vía ollama junto con el contexto.
* Se recibe respuesta → se reproduce usando Coqui TTS.

### 3. Almacenamiento

* Se pueden guardar transcripciones y documentos manualmente desde la interfaz.

---

## 📚 Embeddings y RAG

* Los documentos se procesan con el modelo `sentence-transformers/all-MiniLM-L6-V2` local.
* Se almacenan en una tabla `embeddings` vinculada a cada documento.
* Cuando el usuario realiza una pregunta, se recupera el contexto más relevante vía `cosine_similarity`.

---

## 🗑️ Gestión de documentos y transcripciones

* En la interfaz puedes:

  * Ver transcripciones por páginas
  * Expandir texto largo
  * Editar o eliminar documentos con confirmación
  * Cargar archivos `.txt` y `.docx` como conocimiento nuevo

---

## ⚠️ Requisitos adicionales

* `ffmpeg` debe estar instalado para que Whisper funcione correctamente.
* `ollama` debe estar instalado y funcionando (ej. `ollama run gemma3`).
* Se recomienda usar **Python 3.9+**


1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/JTRC83/asistente_virtual_fausto.git