"""Reglas de seguridad que el hook revisa en el código del login (Python y JavaScript)."""
import re

REGLAS = {
    ".py": {
        r"\.execute(?:many)?\(\s*f[\"']": "SQL armado con f-string (inyección SQL): usa parámetros '?'",
        r"\.execute(?:many)?\([^)\n]*[\"']\s*(?:%|\+)": "SQL armado con % o + (inyección SQL): usa parámetros '?'",
        r"\.execute(?:many)?\([^)\n]*\.format\(": "SQL armado con .format() (inyección SQL): usa parámetros '?'",
        r"hashlib\.(?:md5|sha1)\(": "hash débil (md5/sha1) para contraseñas: usa pbkdf2_hmac con sal",
        r"^\s*import random\b|\brandom\.(?:random|randint|choice)\(": "'random' no es seguro para tokens: usa 'secrets'",
        r"\beval\(|\bexec\(": "eval/exec ejecuta código arbitrario",
    },
    ".js": {
        r"\.innerHTML\s*=": "innerHTML con datos puede causar XSS: usa textContent",
        r"\beval\(": "eval ejecuta código arbitrario",
        r"localStorage\.setItem\([^)]*password": "no guardes contraseñas en localStorage",
    },
}


def revisar(ruta, contenido):
    """Devuelve una lista de problemas 'archivo:línea → motivo' (vacía si todo está bien)."""
    extension = "." + str(ruta).rsplit(".", 1)[-1].lower()
    problemas = []
    for numero, linea in enumerate(contenido.splitlines(), 1):
        if linea.lstrip().startswith(("#", "//")):
            continue  # los comentarios no se ejecutan
        for patron, motivo in REGLAS.get(extension, {}).items():
            if re.search(patron, linea):
                problemas.append(f"{ruta}:{numero} → {motivo}")
    return problemas


if __name__ == "__main__":
    # Uso en CI: python hooks/seguridad.py proyecto-login  → exit 1 si hay problemas
    import sys
    from pathlib import Path

    sys.stdout.reconfigure(encoding="utf-8")
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    archivos = [a for a in sorted(carpeta.rglob("*")) if a.suffix in REGLAS and "tests" not in a.parts]
    encontrados = [p for a in archivos for p in revisar(a.as_posix(), a.read_text(encoding="utf-8"))]
    print("\n".join(encontrados) or f"Seguridad OK: {len(archivos)} archivos revisados en {carpeta}")
    sys.exit(1 if encontrados else 0)
