# test_db.py

from database import guardar_conversacion, guardar_conocimiento, obtener_conversaciones, obtener_conocimientos

def test_guardar_y_leer_conversaciones():
    print("\n== Guardando conversación ==")
    guardar_conversacion("Esta es una conversación de prueba.")

    print("\n== Leyendo conversaciones guardadas ==")
    conversaciones = obtener_conversaciones()
    for c in conversaciones:
        print(f"ID: {c['id']}, Fecha: {c['fecha']}, Texto: {c['texto']}")

def test_guardar_y_leer_conocimientos():
    print("\n== Guardando conocimiento ==")
    guardar_conocimiento("Inteligencia Artificial", "Alan Turing", "El padre de la IA moderna.")

    print("\n== Leyendo conocimientos guardados ==")
    conocimientos = obtener_conocimientos()
    for k in conocimientos:
        print(f"ID: {k['id']}, Tema: {k['tema']}, Autor: {k['autor']}, Texto: {k['texto']}")

if __name__ == "__main__":
    test_guardar_y_leer_conversaciones()
    test_guardar_y_leer_conocimientos()