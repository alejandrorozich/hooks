"""Validacion previa al push para los hooks de los agentes; no ejecuta Git."""
import re
import subprocess
import sys

from proyectos import PROYECTOS, ejecutar_pruebas


def verificar_push(comando):
    # Incluye git push, git.exe push y opciones globales como git -C ruta push.
    if not re.search(r"\bgit(?:\.exe)?\b[^\r\n;&|]*\bpush\b", comando, re.IGNORECASE):
        return

    reportes, bloquear = [], False
    for proyecto in PROYECTOS:
        try:
            ok, salida = ejecutar_pruebas(proyecto)
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"PUSH BLOQUEADO: no se pudieron verificar las pruebas de {proyecto}: {error}", file=sys.stderr)
            sys.exit(2)
        if not ok or not re.search(r"Ran [1-9]\d* tests?\b", salida):
            bloquear = True
        reportes.append(f"── {proyecto} ──\n{salida[-6000:]}")

    if bloquear:
        print(
            "PUSH BLOQUEADO: las pruebas fallaron o no se encontraron pruebas.\n"
            "Corrige el codigo sin modificar los tests. Vuelve a ejecutar las pruebas, "
            "incluye las correcciones en un nuevo commit y reintenta el push.\n\n"
            + "\n\n".join(reportes),
            file=sys.stderr,
        )
        sys.exit(2)

    print("Hook previo al push: pruebas aprobadas; se permite continuar.\n" + "\n\n".join(reportes), file=sys.stderr)
