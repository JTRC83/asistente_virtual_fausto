import sqlite3
import os

# Ruta de la base de datos
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'fausto.db')

def mostrar_conversaciones():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM conversaciones')
    conversaciones = c.fetchall()
    conn.close()

    print("\n=== CONVERSACIONES GUARDADAS ===")
    if conversaciones:
        for conv in conversaciones:
            print(f"ID: {conv[0]} | Fecha: {conv[1]}\nTexto: {conv[2]}\n")
    else:
        print("No hay conversaciones registradas.")

def mostrar_conocimientos():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM conocimientos')
    conocimientos = c.fetchall()
    conn.close()

    print("\n=== CONOCIMIENTOS GUARDADOS ===")
    if conocimientos:
        for con in conocimientos:
            print(f"ID: {con[0]} | Tema: {con[1]} | Autor: {con[2]}\nTexto: {con[3]}\n")
    else:
        print("No hay conocimientos registrados.")

if __name__ == "__main__":
    print("\n¿Qué quieres ver?")
    print("1. Conversaciones")
    print("2. Conocimientos")
    opcion = input("Elige (1 o 2): ")

    if opcion == "1":
        mostrar_conversaciones()
    elif opcion == "2":
        mostrar_conocimientos()
    else:
        print("❌ Opción no válida.")