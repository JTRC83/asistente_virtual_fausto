import sqlite3
import os

# Ruta a la base de datos
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'fausto.db')

def buscar_conversaciones_por_fecha(fecha):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM conversaciones WHERE fecha LIKE ?", ('%' + fecha + '%',))
    resultados = c.fetchall()
    conn.close()
    return resultados

def buscar_conocimientos_por_tema(tema):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM conocimientos WHERE tema LIKE ?", ('%' + tema + '%',))
    resultados = c.fetchall()
    conn.close()
    return resultados

def buscar_conocimientos_por_autor(autor):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM conocimientos WHERE autor LIKE ?", ('%' + autor + '%',))
    resultados = c.fetchall()
    conn.close()
    return resultados

def mostrar_resultados(resultados, tipo):
    if resultados:
        print("\n=== RESULTADOS ENCONTRADOS ===")
        for r in resultados:
            if tipo == "conversacion":
                print(f"ID: {r[0]} | Fecha: {r[1]}\nTexto: {r[2]}\n")
            elif tipo == "conocimiento":
                print(f"ID: {r[0]} | Tema: {r[1]} | Autor: {r[2]}\nTexto: {r[3]}\n")
    else:
        print("⚠ No se encontraron resultados.")

if __name__ == "__main__":
    print("\n¿Qué quieres buscar?")
    print("1. Conversaciones por fecha")
    print("2. Conocimientos por tema")
    print("3. Conocimientos por autor")
    opcion = input("Elige (1, 2 o 3): ")

    if opcion == "1":
        fecha = input("Introduce parte de la fecha (por ejemplo 2025-04): ")
        resultados = buscar_conversaciones_por_fecha(fecha)
        mostrar_resultados(resultados, tipo="conversacion")
    elif opcion == "2":
        tema = input("Introduce parte del tema: ")
        resultados = buscar_conocimientos_por_tema(tema)
        mostrar_resultados(resultados, tipo="conocimiento")
    elif opcion == "3":
        autor = input("Introduce parte del autor: ")
        resultados = buscar_conocimientos_por_autor(autor)
        mostrar_resultados(resultados, tipo="conocimiento")
    else:
        print("❌ Opción no válida.")