"""HOOK 3 · PostToolUse (Edit|Write)
Después de CADA edición a un archivo .py ejecuta las pruebas automáticamente.

Si fallan → exit 2: el resultado le llega a Claude, que se corrige solo.
Si pasan  → exit 0 + JSON con "systemMessage": el usuario ve un aviso verde.
"""
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

datos = json.loads(sys.stdin.buffer.read().decode("utf-8"))
ruta = datos.get("tool_input", {}).get("file_path", "")

if not ruta.endswith(".py"):
    sys.exit(0)  # No es código Python: no hay nada que probar

sys.dont_write_bytecode = True  # evita crear hooks/__pycache__
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
from proyectos import ejecutar_pruebas, proyectos_de

raiz = os.environ.get("CLAUDE_PROJECT_DIR", ".")
fallos, resumenes = [], []
for proyecto in proyectos_de([ruta]):
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

print(json.dumps({"systemMessage": f"✅ Hook de pruebas: {' · '.join(resumenes)} → OK"}, ensure_ascii=False))
sys.exit(0)

# jhvhgvhgdjcaskjXK
# jhvhgvhgdjcaskjXKSSWJQSHSJX
