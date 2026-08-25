"""Regresiones de cadena de suministro y puerta de calidad."""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def test_dependencias_rag_y_analizador_tienen_version_fija():
    produccion = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
    desarrollo = (RAIZ / "requirements-dev.txt").read_text(encoding="utf-8")

    assert re.search(r"^pdfplumber==\d+\.\d+\.\d+$", produccion, re.MULTILINE)
    assert re.search(r"^chromadb==\d+\.\d+\.\d+$", produccion, re.MULTILINE)
    assert re.search(r"^ruff==\d+\.\d+\.\d+$", desarrollo, re.MULTILINE)


def test_ci_corre_estatico_y_pruebas_en_push_y_pull_request():
    workflow = (
        RAIZ / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert "\n  push:" in workflow
    assert "\n  pull_request:" in workflow
    assert "ruff check --select E9,F63,F7,F82 src tests" in workflow
    assert "python -m pytest -q" in workflow
    assert "demostrar_fallo" in workflow
