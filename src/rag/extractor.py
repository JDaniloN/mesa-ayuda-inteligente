"""Lee PDF de políticas sin modificar el archivo original."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

import pdfplumber

from src.rag.modelos import ErrorRag


@dataclass(frozen=True)
class PaginaExtraida:
    numero: int
    texto: str
    tablas: list[list[list[str]]]


@dataclass(frozen=True)
class DocumentoExtraido:
    ruta: Path
    titulo: str
    codigo: str
    version: str
    paginas: list[PaginaExtraida]
    bytes_hash: str


def hash_documentos(rutas: list[Path]) -> str:
    digest = sha256()
    for ruta in sorted(rutas, key=lambda item: item.name.lower()):
        digest.update(ruta.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(ruta.read_bytes())
    return digest.hexdigest()


def extraer_pdf(ruta: Path) -> DocumentoExtraido:
    if not ruta.is_file():
        raise ErrorRag("configuracion", f"No existe el PDF {ruta}.")
    with pdfplumber.open(ruta) as pdf:
        primera = (pdf.pages[0].extract_text() or "") if pdf.pages else ""
        titulo, codigo, version = _cabecera(primera, ruta)
        paginas = []
        for indice, pagina in enumerate(pdf.pages, start=1):
            paginas.append(
                PaginaExtraida(
                    numero=indice,
                    texto=pagina.extract_text() or "",
                    tablas=_limpiar_tablas(pagina.extract_tables() or []),
                )
            )
    return DocumentoExtraido(
        ruta=ruta,
        titulo=titulo,
        codigo=codigo,
        version=version,
        paginas=paginas,
        bytes_hash=sha256(ruta.read_bytes()).hexdigest(),
    )


def extraer_directorio(directorio: Path) -> list[DocumentoExtraido]:
    rutas = sorted(directorio.glob("*.pdf"), key=lambda item: item.name.lower())
    if not rutas:
        raise ErrorRag("configuracion", f"No hay PDF en {directorio}.")
    return [extraer_pdf(ruta) for ruta in rutas]


def _cabecera(texto: str, ruta: Path) -> tuple[str, str, str]:
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    titulo = lineas[0] if lineas else ruta.stem
    hallado = re.search(r"POL-[A-Z]+-\d+", texto)
    codigo = hallado.group(0) if hallado else ruta.stem.split("_")[0]
    version_m = re.search(r"Versi[oó]n\s+(\d+)", texto, re.IGNORECASE)
    version = version_m.group(1) if version_m else "1"
    return titulo, codigo, version


def _limpiar_tablas(tablas: list) -> list[list[list[str]]]:
    limpias = []
    for tabla in tablas:
        filas = []
        for fila in tabla or []:
            celdas = [("" if celda is None else str(celda)).strip() for celda in fila]
            if any(celdas):
                filas.append(celdas)
        if filas:
            limpias.append(filas)
    return limpias
