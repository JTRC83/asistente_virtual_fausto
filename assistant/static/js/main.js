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
  
    // ENVIAR CONOCIMIENTO
    document.getElementById("send-knowledge-btn").addEventListener("click", () => {
      const tema = document.getElementById("theme-select").value;
      const autor = document.getElementById("author-input").value;
      const texto = document.getElementById("knowledge-text").value;
  
      if (!tema || !autor || !texto) {
        alert("Todos los campos deben estar rellenos.");
        return;
      }
  
      socket.emit("guardar_conocimiento", { tema, autor, texto });
    });
  
    socket.on("confirmacion_guardado", (respuesta) => {
      if (respuesta.status === "ok") {
        mostrarAlertaPersonalizada("✅ Conocimiento guardado correctamente 🚀");
        document.getElementById("theme-select").value = "";
        document.getElementById("author-input").value = "";
        document.getElementById("knowledge-text").value = "";
      } else {
        mostrarAlertaPersonalizada("❌ Error al guardar el conocimiento.");
      }
    });
  
    // ✅ GUARDAR TRANSCRIPCIÓN
    document.getElementById("save-transcription-btn").addEventListener("click", () => {
      const texto = document.getElementById("transcription-text").innerText.trim();
  
      if (!texto) {
        alert("No hay ninguna transcripción para guardar.");
        return;
      }
  
      socket.emit("guardar_transcripcion", { texto });
    });
  
    socket.on("confirmacion_transcripcion", (respuesta) => {
      if (respuesta.status === "ok") {
        mostrarAlertaPersonalizada("✅ Transcripción guardada correctamente 📝");
      } else {
        mostrarAlertaPersonalizada("❌ Error al guardar la transcripción.");
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
  
    document.getElementById("cerrar-alerta-btn").addEventListener("click", cerrarAlerta);

    let ordenActual = { columna: null, asc: true };

    function ordenarTabla(campo, thElemento) {
        const tabla = document.getElementById("tabla-conocimientos");
        const filas = Array.from(tabla.querySelectorAll("tr"));
      
        const indice = campo === "tema" ? 0 : 1;
        const ordenActual = thElemento.getAttribute("data-orden") || "asc";
        const nuevoOrden = ordenActual === "asc" ? "desc" : "asc";
        thElemento.setAttribute("data-orden", nuevoOrden);
      
        // Cambiar flecha visualmente
        const flechaSpan = thElemento.querySelector(".flecha");
        if (flechaSpan) {
          flechaSpan.textContent = nuevoOrden === "asc" ? "⬆" : "⬇";
        }
      
        filas.sort((a, b) => {
          const aText = a.children[indice].textContent.toLowerCase();
          const bText = b.children[indice].textContent.toLowerCase();
          return nuevoOrden === "asc" ? aText.localeCompare(bText) : bText.localeCompare(aText);
        });
      
        // Reordenar en DOM
        filas.forEach(f => tabla.appendChild(f));
      }
  
    // MODAL DOCUMENTOS
    function abrirModal() {
      document.getElementById("modal-documentos").classList.remove("hidden");
    }
  
    function cerrarModal() {
      document.getElementById("modal-documentos").classList.add("hidden");
    }
  
    const viewDocsBtn = document.getElementById("view-docs-btn");
    if (viewDocsBtn) {
      viewDocsBtn.addEventListener("click", () => {
        fetch("/obtener_conocimientos")
          .then(res => res.json())
          .then(data => {
            const tbody = document.getElementById("tabla-conocimientos");
            if (tbody) {
              tbody.innerHTML = "";
              data.forEach(doc => {
                const row = document.createElement("tr");
                row.innerHTML = `
                  <td>${doc.tema}</td>
                  <td>${doc.autor}</td>
                  <td>${doc.texto}</td>
                `;
                tbody.appendChild(row);
              });
            }
            const thTema = document.getElementById("th-tema");
            const thAutor = document.getElementById("th-autor");

            if (thTema && thAutor) {
                thTema.addEventListener("click", () => ordenarTabla("tema", thTema));
                thAutor.addEventListener("click", () => ordenarTabla("autor", thAutor));
            }
            abrirModal();
          })
          .catch(err => {
            console.error("Error al obtener documentos:", err);
          });
      });
    }
  
    const cerrarModalBtn = document.getElementById("cerrar-modal");
    if (cerrarModalBtn) {
      cerrarModalBtn.addEventListener("click", cerrarModal);
    }

    socket.on("confirmacion_transcripcion", (respuesta) => {
        if (respuesta.status === "ok") {
          mostrarAlertaPersonalizada("✅ Transcripción guardada correctamente 🚀");        
        } else {
          mostrarAlertaPersonalizada("❌ Error al guardar la transcripción.");
        }
      });
  
      // MODAL HISTORIAL
function abrirModalHistorial() {
    document.getElementById("modal-historial").classList.remove("hidden");
  }
  
  function cerrarModalHistorial() {
    document.getElementById("modal-historial").classList.add("hidden");
  }
  
  const viewHistoryBtn = document.getElementById("view-history-btn");
  if (viewHistoryBtn) {
    viewHistoryBtn.addEventListener("click", () => {
      fetch("/obtener_conversaciones")
        .then(res => res.json())
        .then(data => {
          const tbody = document.getElementById("tabla-historial");
          if (tbody) {
            tbody.innerHTML = "";
            data.forEach(linea => {
              const row = document.createElement("tr");
              row.innerHTML = `
                <td>${linea.fecha}</td>
                <td>${linea.texto}</td>
              `;
              tbody.appendChild(row);
            });
          }
          abrirModalHistorial();
        })
        .catch(err => {
          console.error("Error al cargar historial:", err);
        });
    });
  }
  
  const cerrarHistorialBtn = document.getElementById("cerrar-modal-historial");
  if (cerrarHistorialBtn) {
    cerrarHistorialBtn.addEventListener("click", cerrarModalHistorial);
  }

  // MODAL TEMAS
function abrirModalTemas() {
    document.getElementById("modal-temas").classList.remove("hidden");
  }
  
  function cerrarModalTemas() {
    document.getElementById("modal-temas").classList.add("hidden");
  }
  
  const viewThemesBtn = document.getElementById("view-themes-btn");
  if (viewThemesBtn) {
    viewThemesBtn.addEventListener("click", () => {
      fetch("/estado_temas")
        .then(res => res.json())
        .then(data => {
          const lista = document.getElementById("lista-temas");
          lista.innerHTML = "";
          data.forEach(item => {
            const li = document.createElement("li");
            li.innerHTML = `
              <span>${item.tema}</span>
              <span>${item.estado === "ok" ? "✅" : "❌"}</span>
            `;
            lista.appendChild(li);
          });
          abrirModalTemas();
        })
        .catch(err => console.error("Error al cargar temas:", err));
    });
  }
  
  const cerrarTemasBtn = document.getElementById("cerrar-modal-temas");
  if (cerrarTemasBtn) {
    cerrarTemasBtn.addEventListener("click", cerrarModalTemas);
  }
    // MODAL ARCHIVO
  function abrirModalArchivo() {
    document.getElementById("modal-archivo").classList.remove("hidden");
  }
  
  function cerrarModalArchivo() {
    document.getElementById("modal-archivo").classList.add("hidden");
  }
  
  document.getElementById("upload-file-btn").addEventListener("click", abrirModalArchivo);
  document.getElementById("enviar-archivo-btn").addEventListener("click", () => {
    const tema = document.getElementById("archivo-tema").value;
    const autor = document.getElementById("archivo-autor").value;
    const archivo = document.getElementById("archivo-input").files[0];
  
    if (!tema || !autor || !archivo) {
      alert("Por favor completa todos los campos y selecciona un archivo.");
      return;
    }
  
    const formData = new FormData();
    formData.append("archivo", archivo);
    formData.append("tema", tema);
    formData.append("autor", autor);
  
    fetch("/cargar_archivo", {
      method: "POST",
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === "ok") {
        mostrarAlertaPersonalizada("✅ Archivo procesado y guardado 🚀");
        cerrarModalArchivo();
      } else {
        mostrarAlertaPersonalizada("❌ Error al procesar el archivo");
      }
    })
    .catch(err => {
      console.error("Error al subir el archivo:", err);
      mostrarAlertaPersonalizada("❌ Error inesperado al subir");
    });
  });
    // OTROS BOTONES
    document.getElementById('get-summary-btn').onclick = () => alert("Resumen pendiente");
    
  });

  function cerrarModalArchivo() {
    const modal = document.getElementById("modal-archivo");
    if (modal) {
      modal.classList.add("hidden");
    }
  }