document.addEventListener("DOMContentLoaded", function () {
    // MODO OSCURO
    const toggle = document.getElementById('toggle-theme');
    if (toggle) {
      toggle.addEventListener('change', () => {
        document.body.classList.toggle('dark-mode');
      });
    }
  
    // SOCKET Y MEDIARECORDER
    const socket = io();
    let mediaRecorder;
    const transcriptionText = document.getElementById("transcription-text");
    let audioChunks = [];
  
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = event => {
          if (event.data.size > 0) audioChunks.push(event.data);
        };
        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
          audioChunks = [];
          audioBlob.arrayBuffer().then(buffer => {
            socket.emit("audio_blob", new Uint8Array(buffer));
          });
        };
  
        const convoBtn = document.getElementById("conversation-btn");
        let recording = false;
  
        convoBtn.addEventListener("click", () => {
          recording = !recording;
          convoBtn.classList.toggle("recording", recording);
          if (recording) {
            convoBtn.innerHTML = '<img src="/static/images-icons/mic.png" alt="Mic" class="mic-icon">';
            if (mediaRecorder.state === "inactive") mediaRecorder.start();
          } else {
            convoBtn.innerHTML = '<img src="/static/images-icons/play.png" alt="Play" class="play-icon">';
            if (mediaRecorder.state === "recording") mediaRecorder.stop();
          }
        });
      });
  
    // SOCKET RESPUESTAS
    socket.on("transcription_partial", data => {
      const userLine = document.createElement("div");
      userLine.className = "user-text";
      userLine.innerHTML = `<strong>Usuario:</strong> ${data}`;
      transcriptionText.appendChild(userLine);
    });
  
    socket.on("gemma_response", data => {
      const faustoLine = document.createElement("div");
      faustoLine.className = "fausto-text";
      faustoLine.innerHTML = `<strong>Fausto:</strong> ${data}`;
      transcriptionText.appendChild(faustoLine);
    });
  
    socket.on("gemma_voice", base64Audio => {
      const audio = new Audio("data:audio/wav;base64," + base64Audio);
      audio.play();
    });
  
   // FUNCIONALIDAD ENVIAR CONOCIMIENTO
  document.getElementById("send-knowledge-btn").addEventListener("click", () => {
    const tema = document.getElementById("theme-select").value;
    const autor = document.getElementById("author-input").value;
    const texto = document.getElementById("knowledge-text").value;
  
    if (!tema || !autor || !texto) {
      alert("Todos los campos deben estar rellenos.");
      return;
    }
  
    socket.emit("guardar_conocimiento", {
      tema,
      autor,
      texto
    });
  });

  // ✅ Aquí escuchamos solo una vez la confirmación
  socket.on("confirmacion_guardado", (respuesta) => {
    if (respuesta.status === "ok") {
        mostrarAlertaPersonalizada("✅ Conocimiento guardado correctamente 🚀");
      
        // 🔄 Limpiar los campos después de guardar
        document.getElementById("theme-select").value = "";
        document.getElementById("author-input").value = "";
        document.getElementById("knowledge-text").value = "";
      } else {
      mostrarAlertaPersonalizada("❌ Error al guardar el conocimiento.");
    }
  });

  // FUNCIONES ALERTA
  function mostrarAlertaPersonalizada(mensaje) {
    const alertDiv = document.getElementById("custom-alert");
    document.getElementById("alert-text").textContent = mensaje;
    alertDiv.classList.remove("hidden");
  }

  function cerrarAlerta() {
    const alerta = document.getElementById("custom-alert");
    if (alerta) {
      alerta.classList.add("hidden");
    }
  }

  // Botón para cerrar la alerta
  document.getElementById("cerrar-alerta-btn").addEventListener("click", cerrarAlerta);
  // OTROS BOTONES
  document.getElementById('get-summary-btn').onclick = () => alert("Resumen pendiente");
  document.getElementById('upload-file-btn').onclick = () => alert("Carga de archivo pendiente");
});
  
    
