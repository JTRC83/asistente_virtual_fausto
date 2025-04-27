# database/__init__.py

# Importamos directamente las funciones que más vas a usar
from .db_manager import (
    guardar_conversacion,
    guardar_conocimiento,
    obtener_conversaciones,
    obtener_conocimientos
)
