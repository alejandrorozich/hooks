"""Servidor del login: API JSON + archivos del frontend. Solo usa la librería estándar.

Uso:  python servidor.py  →  http://localhost:8000
Variables opcionales: PORT (puerto) y LOGIN_DB (ruta de la base SQLite).
"""
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import auth
import db

ESTATICOS = Path(__file__).with_name("static")
ARCHIVOS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/static/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/static/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
RUTA_DB = os.environ.get("LOGIN_DB", db.RUTA_POR_DEFECTO)
MAX_CUERPO = 10_000


class Manejador(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/perfil":
            return self.con_base(self.perfil, {})
        if self.path not in ARCHIVOS:
            return self.responder(404, {"error": "Ruta no encontrada"})
        nombre, tipo = ARCHIVOS[self.path]
        self.enviar(200, (ESTATICOS / nombre).read_bytes(), tipo)

    def do_POST(self):
        acciones = {"/api/registro": self.registro, "/api/login": self.login, "/api/logout": self.logout}
        if self.path not in acciones:
            return self.responder(404, {"error": "Ruta no encontrada"})
        try:
            datos = self.leer_json()
        except ValueError as error:
            return self.responder(400, {"error": str(error)})
        self.con_base(acciones[self.path], datos)

    # ── Acciones de la API ────────────────────────────────────────────────
    def registro(self, conexion, datos):
        usuario = auth.registrar_usuario(
            conexion, str(datos.get("nombre", "")), str(datos.get("email", "")), str(datos.get("password", ""))
        )
        self.responder(201, {"usuario": usuario})

    def login(self, conexion, datos):
        sesion = auth.iniciar_sesion(conexion, str(datos.get("email", "")), str(datos.get("password", "")))
        if sesion is None:
            return self.responder(401, {"error": "Email o contraseña incorrectos"})
        self.responder(200, sesion)

    def logout(self, conexion, _datos):
        auth.cerrar_sesion(conexion, self.token())
        self.responder(200, {"ok": True})

    def perfil(self, conexion, _datos):
        usuario = auth.usuario_por_token(conexion, self.token())
        if usuario is None:
            return self.responder(401, {"error": "Sesión inválida o expirada"})
        self.responder(200, {"usuario": usuario})

    # ── Utilidades ────────────────────────────────────────────────────────
    def con_base(self, accion, datos):
        """Abre una conexión por petición y convierte los errores de negocio en 400."""
        conexion = db.conectar(RUTA_DB)
        try:
            accion(conexion, datos)
        except auth.ErrorAuth as error:
            self.responder(400, {"error": str(error)})
        except sqlite3.IntegrityError:
            self.responder(400, {"error": "Ya existe una cuenta con ese email"})
        finally:
            conexion.close()

    def token(self):
        cabecera = self.headers.get("Authorization", "")
        return cabecera.removeprefix("Bearer ").strip()

    def leer_json(self):
        largo = int(self.headers.get("Content-Length") or 0)
        if largo > MAX_CUERPO:
            raise ValueError("Petición demasiado grande")
        try:
            datos = json.loads(self.rfile.read(largo) or b"{}")
        except json.JSONDecodeError:
            raise ValueError("JSON inválido") from None
        if not isinstance(datos, dict):
            raise ValueError("Se esperaba un objeto JSON")
        return datos

    def responder(self, codigo, cuerpo):
        self.enviar(codigo, json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def enviar(self, codigo, contenido, tipo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(contenido)


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 8000))
    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
    print(f"Login en http://localhost:{puerto}  (Ctrl+C para detener)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
