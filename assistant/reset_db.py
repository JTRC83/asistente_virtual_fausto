import sqlite3
import os

# Ruta donde está la base de datos
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'fausto.db')

def resetear_base_datos():
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print("🗑️ Base de datos eliminada.")

    # Ahora recreamos las tablas como en init_db
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS conversaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            texto TEXT NOT NULL
        )
    ''')

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
    print("✅ Base de datos recreada.")

if __name__ == "__main__":
    resetear_base_datos()