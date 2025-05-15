# Importación de librerías estándar necesarias para manejo de BD, rutas, fechas y JSON
import sqlite3
from datetime import datetime
import os
import json

# Ruta absoluta a la base de datos SQLite
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(CURRENT_DIR, 'fausto.db')

# Inicializa la base de datos y crea las tablas si no existen
def inicializar_base_de_datos():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

# Tabla para guardar transcripciones de voz
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        texto TEXT NOT NULL
    )
    ''')

# Tabla para almacenar documentos cargados por el usuario
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conocimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT NOT NULL,
        autor TEXT NOT NULL,
        texto TEXT NOT NULL
    )
    ''')
# Añade columna de control de embeddings si no existe
    try:
        cursor.execute("ALTER TABLE conocimientos ADD COLUMN procesado INTEGER DEFAULT 0")
    except sqlite3.OperationalError as e:
        if "duplicate column name: procesado" not in str(e):
            raise

    # Tabla para almacenar los vectores de embeddings junto con su id de conocimiento
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_conocimiento INTEGER NOT NULL,
        vector TEXT NOT NULL,
        FOREIGN KEY (id_conocimiento) REFERENCES conocimientos(id)
    )
    ''')

    conn.commit()
    conn.close()

# Función para guardar una conversación
# Guarda una transcripción de audio en la tabla conversaciones
def guardar_conversacion(texto):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO conversaciones (fecha, texto) VALUES (?, ?)', (fecha, texto))
    conn.commit()
    conn.close()

# Función para guardar un conocimiento
# Guarda un nuevo documento en la tabla conocimientos
def guardar_conocimiento(tema, autor, texto):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conocimientos (tema, autor, texto)
        VALUES (?, ?, ?)
    """, (tema, autor, texto))

    conn.commit()
    conn.close()

# Función para obtener todas las conversaciones guardadas
# Devuelve todas las conversaciones almacenadas
def obtener_conversaciones():
    """Devuelve todas las conversaciones guardadas"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM conversaciones')
    resultados = c.fetchall()
    conn.close()
    return resultados

# Función para obtener los conocimientos guardados
# Devuelve todos los conocimientos almacenados
def obtener_conocimientos():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, tema, autor, texto FROM conocimientos')
    filas = c.fetchall()
    conn.close()
    return [dict(fila) for fila in filas]

# Función para borrar una conversación
# Borra una transcripción de la tabla conversaciones
def borrar_transcripcion(id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversaciones WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# Función para borrar un conocimiento
# Borra un conocimiento identificándolo por sus campos tema, autor y texto
def borrar_conocimiento(tema, autor, texto):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conocimientos WHERE tema=? AND autor=? AND texto=?", (tema, autor, texto))
    conn.commit()
    conn.close()

# Función para editar un conocimiento
# Permite modificar los campos de un conocimiento, identificándolo por sus valores antiguos
def editar_conocimiento(tema_antiguo, autor_antiguo, texto_antiguo, nuevo_tema, nuevo_autor, nuevo_texto):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE conocimientos
        SET tema = ?, autor = ?, texto = ?
        WHERE tema = ? AND autor = ? AND texto = ?
    """, (nuevo_tema, nuevo_autor, nuevo_texto, tema_antiguo, autor_antiguo, texto_antiguo))
    conn.commit()
    conn.close()

# Función para obtener el estado de RAG
# Devuelve todos los conocimientos junto a su estado de procesamiento (procesado o no)
def obtener_estado_rag():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, tema, autor, texto, procesado FROM conocimientos')
    filas = c.fetchall()
    conn.close()
    return [dict(f) for f in filas]

# Función para obtener los embeddings
# Devuelve los embeddings junto con el texto original asociado
# Se usa para hacer recuperación de contexto vía similitud de coseno
def obtener_embeddings():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.vector, c.texto, c.autor, c.tema 
        FROM embeddings e
        JOIN conocimientos c ON c.id = e.id_conocimiento
    """)
    resultados = cursor.fetchall()
    conn.close()

    return [
        (json.loads(row["vector"]), row["texto"], row["autor"], row["tema"])
        for row in resultados
    ]

# Busca en la base de datos conocimientos por autor o tema
# Devuelve una lista de resultados y el tipo de búsqueda (tema o autor)
def buscar_por_autor_o_tema(termino):
    conn = sqlite3.connect('database/fausto.db')
    cur = conn.cursor()

    # Buscar por tema
    cur.execute("SELECT autor, texto FROM conocimientos WHERE tema LIKE ?", ('%' + termino + '%',))
    resultados_tema = [{"autor": r[0], "texto": r[1]} for r in cur.fetchall()]

    if resultados_tema:
        return resultados_tema, "tema"

    # Buscar por autor
    cur.execute("SELECT tema, texto FROM conocimientos WHERE autor LIKE ?", ('%' + termino + '%',))
    resultados_autor = [{"tema": r[0], "texto": r[1]} for r in cur.fetchall()]
    conn.close()

    if resultados_autor:
        return resultados_autor, "autor"

    return [], None

# Función para borrar todos los embeddings
def borrar_todos_los_embeddings():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # 🧠 Activar integridad referencial
    cursor = conn.cursor()
    cursor.execute("DELETE FROM embeddings")
    cursor.execute("UPDATE conocimientos SET procesado = 0")
    conn.commit()
    conn.close()