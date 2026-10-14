"""Proyectos con pruebas que vigilan los hooks de los agentes (Claude Code, Codex y Git push)."""
from pathlib import Path
import os
import subprocess
import sys

RAIZ = Path(__file__).resolve().parents[1]
PROYECTOS = ["proyecto-demo", "proyecto-login"]


def proyectos_de(rutas):
    """Proyectos que contienen alguna de las rutas editadas; si ninguna cae en uno, todos."""
    rutas = [str(r).replace("\\", "/") for r in rutas]
    tocados = [p for p in PROYECTOS if any(f"{p}/" in r for r in rutas)]
    return tocados or list(PROYECTOS)


def ejecutar_pruebas(proyecto, raiz=RAIZ):
    """Ejecuta unittest en un proyecto. Devuelve (ok, reporte)."""
    resultado = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"],
        cwd=Path(raiz) / proyecto,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},  # tildes y ñ legibles en Windows
        timeout=50,
    )
    return resultado.returncode == 0, resultado.stderr.strip()  # unittest escribe su reporte en stderr
