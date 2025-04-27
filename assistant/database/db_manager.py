import sqlite3
from datetime import datetime
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'fausto.db')

# guardar_conversacion, guardar_conocimiento, obtener_conversaciones, etc.
# Conexión y creación de la base de datos
conn = sqlite3.connect('fausto.db')
cursor = conn.cursor()

# Crear tabla de conversaciones
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    texto TEXT NOT NULL
)
''')

# Crear tabla de conocimientos
cursor.execute('''
CREATE TABLE IF NOT EXISTS conocimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tema TEXT NOT NULL,
    autor TEXT NOT NULL,
    texto TEXT NOT NULL
)
''')

# Confirmamos cambios
conn.commit()

# Función para guardar una conversación
def guardar_conversacion(texto):
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO conversaciones (fecha, texto) VALUES (?, ?)', (fecha, texto))
    conn.commit()

# Función para guardar un conocimiento
def guardar_conocimiento(tema, autor, texto):
    cursor.execute('INSERT INTO conocimientos (tema, autor, texto) VALUES (?, ?, ?)', (tema, autor, texto))
    conn.commit()

def obtener_conversaciones():
    """Devuelve todas las conversaciones guardadas"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM conversaciones')
    resultados = c.fetchall()
    conn.close()
    return resultados

def obtener_conocimientos():
    """Devuelve todos los conocimientos guardados"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM conocimientos')
    resultados = c.fetchall()
    conn.close()
    return resultados

# Función para listar conversaciones
def listar_conversaciones():
    cursor.execute('SELECT * FROM conversaciones ORDER BY fecha DESC')
    return cursor.fetchall()

# Función para listar conocimientos
def listar_conocimientos():
    cursor.execute('SELECT * FROM conocimientos ORDER BY id DESC')
    return cursor.fetchall()

# Al final: cerrar conexión si quieres (opcional cuando uses en app grande)
# conn.close()

# Ejemplo de uso (BORRARLO luego si quieres integrar en Flask directamente)
if __name__ == "__main__":
    guardar_conversacion("Esta es una conversación de prueba.")
    guardar_conocimiento("Inteligencia Artificial", "John McCarthy", "La IA es la simulación de procesos de inteligencia humana por máquinas.")

    print("\nConversaciones:")
    for c in listar_conversaciones():
        print(c)

    print("\nConocimientos:")
    for k in listar_conocimientos():
        print(k)
