"""HOOK 5 · PostToolUse (Edit|Write)
Revisa el código del login después de cada edición: inyección SQL, hashes débiles, tokens con
'random', eval y XSS (innerHTML).

Si encuentra algo → exit 2: el reporte le llega a Claude, que lo corrige solo.
Si está limpio   → exit 0 en silencio.
"""
import json
import sys
from pathlib import Path

sys.stderr.reconfigure(encoding="utf-8")

datos = json.loads(sys.stdin.buffer.read().decode("utf-8"))
ruta = datos.get("tool_input", {}).get("file_path", "")

if "proyecto-login" not in ruta.replace("\\", "/") or not ruta.endswith((".py", ".js")):
    sys.exit(0)  # Solo se vigila el código del login

sys.dont_write_bytecode = True  # evita crear hooks/__pycache__
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
from seguridad import revisar

archivo = Path(ruta)
problemas = revisar(archivo.name, archivo.read_text(encoding="utf-8")) if archivo.exists() else []

if problemas:
    print(
        "🔒 El hook de seguridad encontró problemas en tu cambio. Corrígelos:\n" + "\n".join(problemas),
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
