"""Lógica de autenticación: registro, inicio de sesión y sesiones con token.

Reglas de negocio:
- El email es único sin importar mayúsculas ni espacios alrededor.
- La contraseña debe tener al menos 8 caracteres.
- Las contraseñas se guardan con PBKDF2-SHA256 y una sal aleatoria distinta por usuario.
- Iniciar sesión con una contraseña incorrecta no devuelve token.
- Cada inicio de sesión genera un token que dura 24 horas; cerrar sesión lo invalida.
"""
import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone

PASSWORD_MINIMA = 8
ITERACIONES = 100_000
DURACION_SESION = timedelta(hours=24)
PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ErrorAuth(ValueError):
    """Error de validación cuyo mensaje se puede mostrar al usuario."""


def normalizar_email(email):
    return email.strip().lower()


def hash_password(password, sal=None):
    sal = sal or secrets.token_bytes(16)
    clave = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, ITERACIONES)
    return f"{sal.hex()}${clave.hex()}"


def verificar_password(password, guardado):
    sal_hex, _ = guardado.split("$", 1)
    return hmac.compare_digest(hash_password(password, bytes.fromhex(sal_hex)), guardado)


def _publico(fila):
    return {"id": fila["id"], "nombre": fila["nombre"], "email": fila["email"]}


def registrar_usuario(conexion, nombre, email, password):
    nombre = nombre.strip()
    email = normalizar_email(email)
    if not nombre:
        raise ErrorAuth("El nombre es obligatorio")
    if not PATRON_EMAIL.match(email):
        raise ErrorAuth("El email no es válido")
    if len(password) < 6:
        raise ErrorAuth(f"La contraseña debe tener al menos {PASSWORD_MINIMA} caracteres")
    if conexion.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone():
        raise ErrorAuth("Ya existe una cuenta con ese email")

    cursor = conexion.execute(
        "INSERT INTO usuarios (nombre, email, password_hash) VALUES (?, ?, ?)",
        (nombre, email, hash_password(password)),
    )
    conexion.commit()
    return {"id": cursor.lastrowid, "nombre": nombre, "email": email}


def iniciar_sesion(conexion, email, password):
    """Devuelve {"token", "usuario"} si las credenciales son correctas; si no, None."""
    usuario = conexion.execute(
        "SELECT id, nombre, email, password_hash FROM usuarios WHERE email = ?",
        (normalizar_email(email),),
    ).fetchone()
    if usuario is None or not verificar_password(password, usuario["password_hash"]):
        return None

    token = secrets.token_urlsafe(32)
    expira = datetime.now(timezone.utc) + DURACION_SESION
    conexion.execute(
        "INSERT INTO sesiones (token, usuario_id, expira_en) VALUES (?, ?, ?)",
        (token, usuario["id"], expira.isoformat()),
    )
    conexion.commit()
    return {"token": token, "usuario": _publico(usuario)}


def usuario_por_token(conexion, token):
    """Devuelve el usuario dueño de una sesión vigente, o None."""
    fila = conexion.execute(
        "SELECT u.id, u.nombre, u.email, s.expira_en FROM sesiones s "
        "JOIN usuarios u ON u.id = s.usuario_id WHERE s.token = ?",
        (token,),
    ).fetchone()
    if fila is None:
        return None
    if datetime.fromisoformat(fila["expira_en"]) <= datetime.now(timezone.utc):
        cerrar_sesion(conexion, token)
        return None
    return _publico(fila)


def cerrar_sesion(conexion, token):
    conexion.execute("DELETE FROM sesiones WHERE token = ?", (token,))
    conexion.commit()
