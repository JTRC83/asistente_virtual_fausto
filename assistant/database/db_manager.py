import sqlite3
from datetime import datetime
import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(CURRENT_DIR, 'fausto.db')

def inicializar_base_de_datos():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        texto TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conocimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT NOT NULL,
        autor TEXT NOT NULL,
        texto TEXT NOT NULL
    )
    ''')

    try:
        cursor.execute("ALTER TABLE conocimientos ADD COLUMN procesado INTEGER DEFAULT 0")
    except sqlite3.OperationalError as e:
        if "duplicate column name: procesado" not in str(e):
            raise

    # ✔ Aquí fuera del except
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
def guardar_conversacion(texto):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO conversaciones (fecha, texto) VALUES (?, ?)', (fecha, texto))
    conn.commit()
    conn.close()

# Función para guardar un conocimiento
def guardar_conocimiento(tema, autor, texto):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conocimientos (tema, autor, texto)
        VALUES (?, ?, ?)
    """, (tema, autor, texto))

    conn.commit()
    conn.close()

def obtener_conversaciones():
    """Devuelve todas las conversaciones guardadas"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM conversaciones')
    resultados = c.fetchall()
    conn.close()
    return resultados

def obtener_conocimientos():
    """Devuelve todos los conocimientos guardados como lista de diccionarios"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder como diccionario
    c = conn.cursor()
    c.execute('SELECT tema, autor, texto FROM conocimientos')
    filas = c.fetchall()
    conn.close()

    return [dict(fila) for fila in filas]

# Función para borrar una conversación
def borrar_transcripcion(id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversaciones WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# Función para borrar un conocimiento
def borrar_conocimiento(tema, autor, texto):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conocimientos WHERE tema=? AND autor=? AND texto=?", (tema, autor, texto))
    conn.commit()
    conn.close()

# Función para editar un conocimiento
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
def obtener_estado_rag():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, tema, autor, texto, procesado FROM conocimientos')
    filas = c.fetchall()
    conn.close()
    return [dict(f) for f in filas]

# Función para obtener los embeddings
def obtener_embeddings():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.vector, c.texto 
        FROM embeddings e
        JOIN conocimientos c ON c.id = e.id_conocimiento
    """)
    resultados = cursor.fetchall()
    conn.close()

    # Convertir JSON string a lista
    return [(json.loads(row["vector"]), row["texto"]) for row in resultados]