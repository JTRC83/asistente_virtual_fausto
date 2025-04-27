import sqlite3
import os

# Ruta donde tienes tu base de datos
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'fausto.db')

def crear_tablas():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Crear tabla de conversaciones
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            texto TEXT NOT NULL
        )
    ''')

    # Crear tabla de conocimientos
    c.execute('''
        CREATE TABLE IF NOT EXISTS conocimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema TEXT NOT NULL,
            autor TEXT NOT NULL,
            texto TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_tablas()
    print("✅ Tablas creadas o ya existentes.")