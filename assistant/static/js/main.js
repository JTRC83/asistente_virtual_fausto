
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
    
      // BOTONES EXTRA
      document.getElementById('get-summary-btn').onclick = () => alert("Resumen pendiente");
      document.getElementById('send-knowledge-btn').onclick = () => alert("Texto enviado");
      document.getElementById('upload-file-btn').onclick = () => alert("Carga de archivo pendiente");
    
      // RIGHT SIDEBAR
      const toggleBtn = document.getElementById("toggle-right-sidebar");
      const sidebarContent = document.getElementById("right-sidebar-content");
      if (toggleBtn) {
        toggleBtn.addEventListener("click", function() {
          sidebarContent.style.display = (sidebarContent.style.display === "none" || sidebarContent.style.display === "") ? "flex" : "none";
        });
      }
    });
