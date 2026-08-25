"""Fragmentación estructural con IDs determinísticos."""

from __future__ import annotations

from hashlib import sha256
import re
import unicodedata

from src.rag.extractor import DocumentoExtraido
from src.rag.modelos import Fragmento
from src.rag.parser import parsear_documento

MAX_TOKENS = 800
MIN_PARTIR = 500


def fragmentar_documento(documento: DocumentoExtraido) -> list[Fragmento]:
    fragmentos: list[Fragmento] = []
    for bloque in parsear_documento(documento):
        partes = _partir_si_grande(bloque.texto)
        for parte in partes:
            texto = parte.strip()
            if not texto:
                continue
            chunk_id = id_fragmento(
                documento.codigo,
                documento.version,
                bloque.seccion,
                texto,
            )
            fragmentos.append(
                Fragmento(
                    chunk_id=chunk_id,
                    codigo=documento.codigo,
                    titulo_documento=documento.titulo,
                    version=documento.version,
                    seccion=bloque.seccion,
                    seccion_padre=bloque.seccion_padre,
                    titulo_seccion=bloque.titulo_seccion,
                    pagina_inicio=bloque.pagina_inicio,
                    pagina_fin=bloque.pagina_fin,
                    texto=texto,
                )
            )
    return fragmentos


def id_fragmento(codigo: str, version: str, seccion: str, texto: str) -> str:
    base = "|".join(
        [codigo.strip(), version.strip(), seccion.strip(), _normalizar(texto)]
    )
    return sha256(base.encode("utf-8")).hexdigest()


def _normalizar(texto: str) -> str:
    nfc = unicodedata.normalize("NFC", texto or "")
    return re.sub(r"\s+", " ", nfc).strip()


def _tokens_estimados(texto: str) -> int:
    return max(1, len(texto) // 4)


def _partir_si_grande(texto: str) -> list[str]:
    if _tokens_estimados(texto) <= MAX_TOKENS:
        return [texto]
    parrafos = [parte.strip() for parte in re.split(r"\n{2,}|\n", texto) if parte.strip()]
    actual: list[str] = []
    partes: list[str] = []
    for parrafo in parrafos:
        candidato = "\n".join(actual + [parrafo])
        if actual and _tokens_estimados(candidato) > MAX_TOKENS:
            partes.append("\n".join(actual))
            actual = [parrafo]
        else:
            actual.append(parrafo)
    if actual:
        partes.append("\n".join(actual))
    return partes or [texto]
