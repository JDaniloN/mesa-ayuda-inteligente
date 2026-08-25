"""Contratos internos del RAG: fragmentos, hits y consulta."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


MENSAJE_ABSTENCION = (
    "No encontré información suficiente en las políticas proporcionadas "
    "para responder la pregunta."
)


@dataclass(frozen=True)
class Fragmento:
    chunk_id: str
    codigo: str
    titulo_documento: str
    version: str
    seccion: str
    seccion_padre: str
    titulo_seccion: str
    pagina_inicio: int
    pagina_fin: int
    texto: str


@dataclass(frozen=True)
class Hit:
    texto: str
    score: float
    metadata: dict
    vector_score: float = 0.0
    lexical_score: float = 0.0
    source_queries: tuple[str, ...] = ()
    retrieval_type: str = "direct"


@dataclass
class ResultadoRecuperacion:
    hits: list[Hit]
    coverage: dict
    subconsultas: dict


@dataclass
class ResultadoConsulta:
    respuesta: str
    citas: list[dict] = field(default_factory=list)
    abstuvo: bool = False
    hits: list[Hit] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)


class ErrorRag(Exception):
    """Fallo controlado de configuración o índice; la API lo traduce a HTTP."""

    def __init__(self, codigo: str, mensaje: str, status: int = 503) -> None:
        self.codigo = codigo
        self.mensaje = mensaje
        self.status = status
        super().__init__(mensaje)


class PuertoEmbeddings:
    modelo: str

    def embed(self, textos: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def close(self) -> None:
        return None


class PuertoGenerador:
    def generar(
        self,
        pregunta: str,
        contextos: list[str],
        cobertura: dict | None = None,
    ) -> str:
        raise NotImplementedError

    def close(self) -> None:
        return None
