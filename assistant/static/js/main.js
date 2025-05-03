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

      // ✅ RESET DE TRANSCRIPCIÓN (sin alerta)
      const resetBtn = document.getElementById("reset-transcription-btn");
      if (resetBtn) {
        resetBtn.addEventListener("click", () => {
          const contenedor = document.getElementById("transcription-text");
          if (contenedor) {
            contenedor.innerHTML = "";
          }
        });
      }
  
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
  
    // MODAL HISTORIAL CON PAGINACIÓN Y VER MÁS / VER MENOS
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
      .then(historial => {  // <-- usar un nombre distinto aquí
        let currentPage = 1;
        const itemsPerPage = 5;
        const totalPages = () => Math.ceil(historial.length / itemsPerPage);

        function renderPage(page) {
          const tbody = document.getElementById("tabla-historial");
          tbody.innerHTML = "";
          const start = (page - 1) * itemsPerPage;
          const end = start + itemsPerPage;
          const pageItems = historial.slice(start, end);

          pageItems.forEach(linea => {
            const row = document.createElement("tr");
            const textoCorto = linea.texto.length > 300 ? linea.texto.substring(0, 300) + "..." : linea.texto;

            row.innerHTML = `
              <td>${linea.fecha}</td>
              <td>
                <div id="texto-${linea.id}" class="transcripcion-truncada">${textoCorto}</div>
                ${linea.texto.length > 300 ? `
                  <button class="btn-expandir round-btn" data-id="${linea.id}" data-full="${encodeURIComponent(linea.texto)}" title="Ver más">...</button>` : ""}
              </td>
              <td>
                <button class="round-btn btn-borrar-transcripcion" data-id="${linea.id}" title="Borrar">
                  <img src="/static/images-icons/basura.png" alt="Borrar">
                </button>
              </td>
            `;
            tbody.appendChild(row);
          });

          // Botón ver más / ver menos
          document.querySelectorAll(".btn-expandir").forEach(btn => {
            btn.addEventListener("click", () => {
              const id = btn.getAttribute("data-id");
              const div = document.getElementById(`texto-${id}`);
              const isExpanded = btn.getAttribute("data-expanded") === "true";
              if (isExpanded) {
                div.classList.add("transcripcion-truncada");
                div.textContent = decodeURIComponent(btn.getAttribute("data-full")).substring(0, 300) + "...";
                btn.textContent = "...";
                btn.setAttribute("data-expanded", "false");
              } else {
                div.classList.remove("transcripcion-truncada");
                div.textContent = decodeURIComponent(btn.getAttribute("data-full"));
                btn.textContent = "▲";
                btn.setAttribute("data-expanded", "true");
              }
            });
          });

          // Botón borrar con confirmación
          document.querySelectorAll(".btn-borrar-transcripcion").forEach(btn => {
            btn.addEventListener("click", () => {
              const id = parseInt(btn.getAttribute("data-id"));
              mostrarConfirmacionPersonalizada("¿Estás seguro de que deseas borrar esta transcripción?", () => {
                fetch(`/borrar_transcripcion/${id}`, { method: "DELETE" })
                  .then(res => res.json())
                  .then(response => {
                    if (response.status === "ok") {
                      mostrarAlertaPersonalizada("✅ Transcripción eliminada 🗑️");
                      const index = historial.findIndex(item => item.id === id);
                      if (index !== -1) historial.splice(index, 1);
                      if (currentPage > totalPages()) currentPage--;
                      renderPage(currentPage);
                    } else {
                      mostrarAlertaPersonalizada("❌ Error al borrar transcripción");
                    }
                  })
                  .catch(err => {
                    console.error("Error al borrar:", err);
                    mostrarAlertaPersonalizada("❌ Error inesperado al borrar");
                  });
              });
            });
          });

          // Paginación
          const controls = document.getElementById("paginacion-historial");
          controls.innerHTML = `
            <button ${page === 1 ? "disabled" : ""} id="prev-page">Anterior</button>
            <span>Página ${page} de ${totalPages()}</span>
            <button ${page === totalPages() ? "disabled" : ""} id="next-page">Siguiente</button>
          `;
          document.getElementById("prev-page").onclick = () => {
            if (currentPage > 1) {
              currentPage--;
              renderPage(currentPage);
            }
          };
          document.getElementById("next-page").onclick = () => {
            if (currentPage < totalPages()) {
              currentPage++;
              renderPage(currentPage);
            }
          };
        }

        renderPage(currentPage);
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

    // ✅ Función para mostrar alerta personalizada
function mostrarAlertaPersonalizada(mensaje) {
  const alertDiv = document.getElementById("custom-alert");
  const texto = document.getElementById("alert-text");
  if (alertDiv && texto) {
    texto.textContent = mensaje;
    alertDiv.classList.remove("hidden");
  }
}

// ✅ Función para mostrar confirmación personalizada
function mostrarConfirmacionPersonalizada(mensaje, accionConfirmada) {
  const modal = document.getElementById("confirm-modal");
  const texto = document.getElementById("confirm-modal-text");
  const btnSi = document.getElementById("confirm-yes-btn");
  const btnNo = document.getElementById("confirm-no-btn");

  texto.textContent = mensaje;
  modal.classList.remove("hidden");

  // Clonar botón "Sí" para evitar múltiples listeners
  const nuevoBtnSi = btnSi.cloneNode(true);
  nuevoBtnSi.id = "confirm-yes-btn"; // Reasignar el ID
  btnSi.parentNode.replaceChild(nuevoBtnSi, btnSi);

  nuevoBtnSi.addEventListener("click", () => {
    modal.classList.add("hidden");
    accionConfirmada();
  });

  btnNo.addEventListener("click", () => {
    modal.classList.add("hidden");
  });
}

// MODAL DOCUMENTOS con paginación y acciones -----------------------------------------
function abrirModalDocumentos() {
  document.getElementById("modal-documentos").classList.remove("hidden");
}

function cerrarModalDocumentos() {
  document.getElementById("modal-documentos").classList.add("hidden");
}

const viewDocsBtn = document.getElementById("view-docs-btn");
if (viewDocsBtn) {
  viewDocsBtn.addEventListener("click", () => {
    fetch("/obtener_conocimientos")
      .then(res => res.json())
      .then(data => {
        let currentPage = 1;
        const itemsPerPage = 5;
        let ordenTemaAsc = true;
        let ordenAutorAsc = true;

        function renderPage(page) {
          const tbody = document.getElementById("tabla-conocimientos");
          tbody.innerHTML = "";
          const start = (page - 1) * itemsPerPage;
          const end = start + itemsPerPage;
          const pageItems = data.slice(start, end);

          pageItems.forEach((doc, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${doc.tema}</td>
              <td>${doc.autor}</td>
              <td>
                <div id="texto-${doc.id}" class="transcripcion-truncada">${doc.texto}</div>
                ${
                  doc.texto.length > 300
                    ? `<button class="round-btn btn-expandir" data-id="${doc.id}" data-full="${encodeURIComponent(doc.texto)}" data-expanded="false" title="Expandir">...</button>`
                    : ""
                }
              </td>        
              <td>
                <div class="acciones-container">
                  <button class="round-btn btn-editar" data-id="${doc.id}" title="Editar">
                    <img src="/static/images-icons/editar.png" alt="Editar">
                  </button>
                  <button class="round-btn btn-borrar-doc"
                          data-id="${doc.id}"
                          data-tema="${encodeURIComponent(doc.tema)}"
                          data-autor="${encodeURIComponent(doc.autor)}"
                          data-texto="${encodeURIComponent(doc.texto)}"
                          title="Borrar">
                    <img src="/static/images-icons/basura.png" alt="Borrar">
                  </button>
                </div>
              </td>
            `;
            tbody.appendChild(row);
          });

          // Botón ver más / ver menos
          document.querySelectorAll(".btn-expandir").forEach(btn => {
            btn.addEventListener("click", () => {
              const id = btn.getAttribute("data-id");
              const div = document.getElementById(`texto-${id}`);
              const isExpanded = btn.getAttribute("data-expanded") === "true";
              if (isExpanded) {
                div.classList.add("transcripcion-truncada");
                btn.textContent = "...";                
                btn.setAttribute("data-expanded", "false");
                btn.setAttribute("title", "Expandir");
              } else {
                div.classList.remove("transcripcion-truncada");
                btn.textContent = "▲";                
                btn.setAttribute("data-expanded", "true");
                btn.setAttribute("title", "Colapsar");
              }
            });
          });

          document.querySelectorAll(".btn-borrar-doc").forEach(btn => {
            btn.addEventListener("click", () => {
              const tema = decodeURIComponent(btn.getAttribute("data-tema"));
              const autor = decodeURIComponent(btn.getAttribute("data-autor"));
              const texto = decodeURIComponent(btn.getAttribute("data-texto"));

              mostrarConfirmacionPersonalizada("¿Estás seguro de que deseas borrar este documento?", () => {
                fetch("/borrar_conocimiento", {
                  method: "DELETE",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ tema, autor, texto })
                })
                  .then(res => res.json())
                  .then(r => {
                    if (r.status === "ok") {
                      mostrarAlertaPersonalizada("✅ Documento eliminado 🗑️");

                      fetch("/obtener_conocimientos")
                        .then(res => res.json())
                        .then(nuevaData => {
                          data = nuevaData;
                          const totalPages = Math.ceil(data.length / itemsPerPage);
                          if (currentPage > totalPages) currentPage = totalPages;
                          renderPage(currentPage);
                        });
                    } else {
                      mostrarAlertaPersonalizada("❌ Error al eliminar");
                    }
                  })
                  .catch(err => {
                    console.error("Error al borrar:", err);
                    mostrarAlertaPersonalizada("❌ Error inesperado al eliminar");
                  });
              });
            });
          });

          document.querySelectorAll(".btn-editar").forEach(btn => {
            btn.addEventListener("click", () => {
              const row = btn.closest("tr");
              const index = Array.from(row.parentNode.children).indexOf(row);

              const temaCell = row.children[0];
              const autorCell = row.children[1];
              const textoCell = row.children[2];
              const accionesCell = row.children[3];

              const temaOriginal = temaCell.textContent.trim();
              const autorOriginal = autorCell.textContent.trim();
              const textoOriginal = textoCell.textContent.trim();

              temaCell.innerHTML = `<input type="text" value="${temaOriginal}" class="input-editar">`;
              autorCell.innerHTML = `<input type="text" value="${autorOriginal}" class="input-editar">`;
              textoCell.innerHTML = `<textarea class="input-editar" style="width: 100%; height: 140px">${textoOriginal}</textarea>`;
              accionesCell.innerHTML = `
                <div class="acciones-container">
                  <button class="round-btn btn-guardar" title="Guardar">
                    <img src="/static/images-icons/guardar.png" alt="Guardar" style="width: 45px; height: 45px;">
                  </button>
                </div>
              `;

              accionesCell.querySelector(".btn-guardar").addEventListener("click", () => {
                const nuevoTema = temaCell.querySelector("input").value;
                const nuevoAutor = autorCell.querySelector("input").value;
                const nuevoTexto = textoCell.querySelector("textarea").value;

                fetch("/editar_conocimiento", {
                  method: "PUT",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    tema: nuevoTema,
                    autor: nuevoAutor,
                    texto: nuevoTexto,
                    original: {
                      tema: temaOriginal,
                      autor: autorOriginal,
                      texto: textoOriginal
                    }
                  })
                })
                  .then(res => res.json())
                  .then(r => {
                    if (r.status === "ok") {
                      mostrarAlertaPersonalizada("✅ Documento actualizado correctamente ✏️");
                      data[index] = {
                        id: data[index].id,
                        tema: nuevoTema,
                        autor: nuevoAutor,
                        texto: nuevoTexto
                      };
                      renderPage(currentPage);
                    } else {
                      mostrarAlertaPersonalizada("❌ Error al guardar");
                    }
                  });
              });
            });
          });

          const controls = document.getElementById("paginacion-documentos");
          const totalPages = Math.ceil(data.length / itemsPerPage);
          controls.innerHTML = `
            <button ${page === 1 ? "disabled" : ""} id="prev-doc">Anterior</button>
            <span>Página ${page} de ${totalPages}</span>
            <button ${page === totalPages ? "disabled" : ""} id="next-doc">Siguiente</button>
          `;

          document.getElementById("prev-doc").onclick = () => {
            if (currentPage > 1) {
              currentPage--;
              renderPage(currentPage);
            }
          };

          document.getElementById("next-doc").onclick = () => {
            if (currentPage < totalPages) {
              currentPage++;
              renderPage(currentPage);
            }
          };
        }

        // Agregar listeners de ordenamiento
        document.getElementById("ordenar-tema")?.addEventListener("click", () => {
          data.sort((a, b) => ordenTemaAsc ? a.tema.localeCompare(b.tema) : b.tema.localeCompare(a.tema));
          ordenTemaAsc = !ordenTemaAsc;
          renderPage(1);
        });

        document.getElementById("ordenar-autor")?.addEventListener("click", () => {
          data.sort((a, b) => ordenAutorAsc ? a.autor.localeCompare(b.autor) : b.autor.localeCompare(a.autor));
          ordenAutorAsc = !ordenAutorAsc;
          renderPage(1);
        });

        renderPage(currentPage);
        abrirModalDocumentos();
      });
  });
}

const cerrarModalDocsBtn = document.getElementById("cerrar-modal");
if (cerrarModalDocsBtn) {
  cerrarModalDocsBtn.addEventListener("click", cerrarModalDocumentos);
}

  // MODAL TEMAS ---------------------------
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

 // ✅ Función para mostrar alerta personalizada
function mostrarAlertaPersonalizada(mensaje) {
    const alertDiv = document.getElementById("custom-alert");
    const texto = document.getElementById("alert-text");
    if (alertDiv && texto) {
      texto.textContent = mensaje;
      alertDiv.classList.remove("hidden");
    }
  }
  
  // ✅ Modal RAG -------------------------------------------------
  function abrirModalRAG() {
    document.getElementById("modal-rag").classList.remove("hidden");
  }
  
  function cerrarModalRAG() {
    document.getElementById("modal-rag").classList.add("hidden");
  }
  
  document.getElementById("cerrar-modal-rag").addEventListener("click", cerrarModalRAG);
  
  document.getElementById("view-rag-btn").addEventListener("click", () => {
    fetch("/estado_rag")
      .then(res => res.json())
      .then(data => {
        let currentPage = 1;
        const itemsPerPage = 5;
        const totalPages = Math.ceil(data.length / itemsPerPage);
  
        function renderPage(page) {
          const tbody = document.getElementById("tabla-rag");
          tbody.innerHTML = "";
          const start = (page - 1) * itemsPerPage;
          const end = start + itemsPerPage;
          const items = data.slice(start, end);
  
          let hayPendientes = false;
  
          items.forEach(item => {
            if (item.procesado === 0) hayPendientes = true; 
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${item.id}</td>
              <td>${item.tema}</td>
              <td>${item.autor}</td>
              <td>${item.texto.split(" ").slice(0, 12).join(" ")}...</td>
              <td style="text-align: center; font-size: 18px;">
                ${item.procesado === 1 ? "✅" : "❌"}
              </td>
            `;
            tbody.appendChild(row);
          });
  
          const btn = document.getElementById("ejecutar-embedding-btn");
          btn.style.display = "inline-block";
  
          const paginacion = document.getElementById("paginacion-rag");
          paginacion.innerHTML = `
            <button ${page === 1 ? "disabled" : ""} id="prev-rag">Anterior</button>
            <span>Página ${page} de ${totalPages}</span>
            <button ${page === totalPages ? "disabled" : ""} id="next-rag">Siguiente</button>
          `;
  
          document.getElementById("prev-rag").onclick = () => {
            if (currentPage > 1) {
              currentPage--;
              renderPage(currentPage);
            }
          };
  
          document.getElementById("next-rag").onclick = () => {
            if (currentPage < totalPages) {
              currentPage++;
              renderPage(currentPage);
            }
          };
        }
  
        renderPage(currentPage);
        abrirModalRAG();
      })
      .catch(err => {
        console.error("Error al cargar estado RAG:", err);
        mostrarAlertaPersonalizada("❌ Error al cargar estado RAG");
      });
  });
  
  // ✅ Ejecutar Embeddings
  const btn = document.getElementById("ejecutar-embedding-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      fetch("/ejecutar_embeddings", { method: "POST" })
        .then(res => res.json())
        .then(data => {
          if (data.status === "ok") {
            mostrarAlertaPersonalizada("✅ " + data.mensaje);
            document.getElementById("view-rag-btn").click(); // Refresca el modal
          } else {
            mostrarAlertaPersonalizada("❌ " + data.mensaje);
          }
        })
        .catch(err => {
          console.error("Error al generar embeddings:", err);
          mostrarAlertaPersonalizada("❌ Error inesperado al generar embeddings");
        });
    });
  }




