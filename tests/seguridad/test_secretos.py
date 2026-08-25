"""Guardas básicas contra secretos en el código desarrollado."""

from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[2]
PATRON_CLAVE_OPENAI = re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}")


def test_env_esta_ignorado():
    ignorados = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in {linea.strip() for linea in ignorados}


def test_codigo_documentacion_y_pruebas_no_contienen_claves_openai():
    archivos = [RAIZ / "README.md", RAIZ / ".env.example"]
    for carpeta in ("src", "tests", "docs"):
        archivos.extend(
            ruta
            for ruta in (RAIZ / carpeta).rglob("*")
            if ruta.is_file() and ruta.suffix in {".py", ".md", ".json", ".yaml", ".yml"}
        )

    hallazgos = [
        str(ruta.relative_to(RAIZ))
        for ruta in archivos
        if PATRON_CLAVE_OPENAI.search(ruta.read_text(encoding="utf-8"))
    ]

    assert hallazgos == []
