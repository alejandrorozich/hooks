"""HOOK 3 (Codex) · PostToolUse (apply_patch)
Después de CADA parche a un archivo .py ejecuta las pruebas automáticamente.

Si fallan → exit 2: Codex reemplaza el resultado de la edición por este reporte y el modelo se corrige.
Si pasan  → JSON con "additionalContext": el modelo sabe que las pruebas pasaron.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

datos = json.loads(sys.stdin.buffer.read().decode("utf-8"))
parche = datos.get("tool_input", {}).get("command", "")
rutas = [r.strip() for r in re.findall(r"^\*\*\* (?:Add|Update) File: (.+)$", parche, re.MULTILINE)]

if not any(r.endswith(".py") for r in rutas):
    sys.exit(0)  # No se tocó código Python: no hay nada que probar

sys.dont_write_bytecode = True  # evita crear hooks/__pycache__
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
from proyectos import ejecutar_pruebas, proyectos_de

# Codex ejecuta el hook en la carpeta de la sesión (C:\UPB\hooks)
raiz = datos.get("cwd") or os.getcwd()
fallos, resumenes = [], []
for proyecto in proyectos_de(rutas):
    ok, salida = ejecutar_pruebas(proyecto, raiz)
    total = next((l for l in salida.splitlines() if l.startswith("Ran ")), "")
    resumenes.append(f"{proyecto}: {total}")
    if not ok:
        fallos.append(f"── {proyecto} ──\n{salida[-6000:]}")

if fallos:
    print(
        "❌ El hook ejecutó las pruebas después de tu cambio y FALLARON.\n"
        "Revisa el error y corrige el código (las pruebas no se pueden modificar):\n\n"
        + "\n\n".join(fallos),
        file=sys.stderr,
    )
    sys.exit(2)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": f"✅ Hook de pruebas: {' · '.join(resumenes)} → OK",
    }
}, ensure_ascii=False))
sys.exit(0)
