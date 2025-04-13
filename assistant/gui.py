import tkinter as tk
from tkinter import scrolledtext, ttk
import webbrowser

# Ruta típica para Google Chrome en macOS
chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# Obtener el navegador Chrome registrado
chrome = webbrowser.get('chrome')


class AsistenteGUI:
    def __init__(self):
        # Ventana principal
        self.root = tk.Tk()
        self.root.title("Asistente Virtual: Fausto")
        self.root.geometry("700x500")
        self.root.minsize(650, 400)
        
        # Aplicar estilo ttk
        self.style = ttk.Style(self.root)
        # Puedes probar distintos temas: 'clam', 'alt', 'default', 'classic'
        self.style.theme_use("clam")  

        # -------- Frame Principal ----------
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # -------- Frame Título ----------
        self.frame_titulo = ttk.Frame(self.main_frame, padding="5 5 5 5")
        self.frame_titulo.pack(fill=tk.X, expand=False)

        self.label_titulo = ttk.Label(self.frame_titulo, text="Fausto - Asistente Virtual", 
                                      font=("Helvetica", 18, "bold"))
        self.label_titulo.pack(side=tk.LEFT)

        # -------- Frame de Conversación ----------
        self.frame_conversacion = ttk.Frame(self.main_frame, padding="5 5 5 5")
        self.frame_conversacion.pack(fill=tk.BOTH, expand=True)

        # Agregamos un Label opcional
        self.label_conversacion = ttk.Label(self.frame_conversacion, text="Conversación:")
        self.label_conversacion.pack(anchor=tk.W, pady=(0,5))

        self.text_area = scrolledtext.ScrolledText(self.frame_conversacion, wrap=tk.WORD, width=70, height=15)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # -------- Frame de Botones ----------
        self.frame_botones = ttk.Frame(self.main_frame, padding="5 5 5 5")
        self.frame_botones.pack(fill=tk.X, expand=False)

        # Botones para Grabar / Parar (por ahora simulamos)
        self.btn_grabar = ttk.Button(self.frame_botones, text="Grabar", command=self.simular_grabacion)
        self.btn_grabar.pack(side=tk.LEFT, padx=(0,10))

        self.btn_parar = ttk.Button(self.frame_botones, text="Parar", command=self.simular_parar)
        self.btn_parar.pack(side=tk.LEFT, padx=(0,10))

        # Botón para salir (opcional)
        self.btn_salir = ttk.Button(self.frame_botones, text="Salir", command=self.root.quit)
        self.btn_salir.pack(side=tk.RIGHT)

    def simular_grabacion(self):
        # Aquí podrías iniciar la grabación real
        self.text_area.insert(tk.END, "Iniciando grabación...\n")

    def simular_parar(self):
        # Aquí podrías detener la grabación real
        self.text_area.insert(tk.END, "Deteniendo grabación...\n")

    def run(self):
        self.root.mainloop()