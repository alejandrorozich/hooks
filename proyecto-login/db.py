"""Conexión a la base de datos SQLite del login y creación de las tablas."""
import sqlite3
from pathlib import Path

RUTA_POR_DEFECTO = Path(__file__).with_name("login.db")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    creado_en     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sesiones (
    token      TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    expira_en  TEXT NOT NULL
);
"""


def conectar(ruta=RUTA_POR_DEFECTO):
    """Abre la base (":memory:" para pruebas), activa claves foráneas y crea las tablas si faltan."""
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.executescript(ESQUEMA)
    return conexion
