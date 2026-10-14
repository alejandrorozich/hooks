"""HOOK 5 (Codex) · PostToolUse (apply_patch)
Revisa el código del login después de cada parche: inyección SQL, hashes débiles, tokens con
'random', eval y XSS (innerHTML). Las rutas vienen en el parche ("*** Update File: ruta").
"""
import json
import os
import re
import sys
from pathlib import Path

sys.stderr.reconfigure(encoding="utf-8")

datos = json.loads(sys.stdin.buffer.read().decode("utf-8"))
parche = datos.get("tool_input", {}).get("command", "")
rutas = [r.strip() for r in re.findall(r"^\*\*\* (?:Add|Update) File: (.+)$", parche, re.MULTILINE)]
rutas = [r for r in rutas if "proyecto-login" in r.replace("\\", "/") and r.endswith((".py", ".js"))]

if not rutas:
    sys.exit(0)  # Solo se vigila el código del login

sys.dont_write_bytecode = True  # evita crear hooks/__pycache__
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
from seguridad import revisar

raiz = Path(datos.get("cwd") or os.getcwd())
problemas = []
for ruta in rutas:
    archivo = raiz / ruta
    if archivo.exists():
        problemas += revisar(archivo.name, archivo.read_text(encoding="utf-8"))

if problemas:
    print(
        "🔒 El hook de seguridad encontró problemas en tu cambio. Corrígelos:\n" + "\n".join(problemas),
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
