"""Embeddings OpenAI-compatibles; nunca se inventan vectores en ejecución real."""

from __future__ import annotations

from hashlib import sha256
import logging
import re
from typing import Optional

import httpx

from src.metricas import RegistroMetricas
from src.rag.modelos import ErrorRag, PuertoEmbeddings

log = logging.getLogger("mesa.rag")


class EmbeddingsHttp(PuertoEmbeddings):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        modelo: str,
        timeout_s: float = 8.0,
        http: Optional[httpx.Client] = None,
        metricas: RegistroMetricas | None = None,
    ) -> None:
        self.modelo = modelo
        self._url = _url_embeddings(base_url)
        self._api_key = api_key
        self._propios = http is None
        self._http = http or httpx.Client(timeout=timeout_s)
        self._metricas = metricas

    def embed(self, textos: list[str]) -> list[list[float]]:
        if not textos:
            return []
        try:
            respuesta = self._http.post(
                self._url,
                json={"model": self.modelo, "input": textos},
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        except httpx.TimeoutException as exc:
            self._registrar_uso(None)
            raise ErrorRag("configuracion", "Timeout al generar embeddings.") from exc
        except httpx.RequestError as exc:
            self._registrar_uso(None)
            raise ErrorRag("configuracion", "No fue posible conectar con embeddings.") from exc
        try:
            cuerpo = respuesta.json()
        except ValueError:
            cuerpo = None
        self._registrar_uso(cuerpo)
        if respuesta.status_code >= 400:
            log.warning(
                "rag_provider_error",
                extra={
                    "event": "rag_provider_error",
                    "operation": "embeddings",
                    "model": self.modelo,
                    "reason": f"http_{respuesta.status_code}",
                },
            )
            raise ErrorRag(
                "configuracion",
                "El proveedor de embeddings no está disponible.",
            )
        try:
            data = cuerpo["data"]
            ordenados = sorted(data, key=lambda item: item["index"])
            return [item["embedding"] for item in ordenados]
        except (KeyError, TypeError, ValueError) as exc:
            raise ErrorRag("configuracion", "Respuesta de embeddings inválida.") from exc

    def _registrar_uso(self, data: dict | None) -> None:
        if self._metricas is not None:
            usage = data.get("usage") if isinstance(data, dict) else None
            self._metricas.registrar_llamada_ia(
                "embeddings",
                self.modelo,
                usage,
            )

    def close(self) -> None:
        if self._propios:
            self._http.close()


class EmbeddingsFalsos(PuertoEmbeddings):
    """Vectores deterministas por n-gramas; solo para pruebas sin red."""

    def __init__(self, modelo: str = "fake-embedding", dim: int = 256) -> None:
        self.modelo = modelo
        self.dim = dim

    def embed(self, textos: list[str]) -> list[list[float]]:
        return [_vector(texto, self.dim) for texto in textos]


def _vector(texto: str, dim: int) -> list[float]:
    valores = [0.0] * dim
    stop = {
        "el",
        "la",
        "los",
        "las",
        "de",
        "del",
        "y",
        "o",
        "a",
        "en",
        "un",
        "una",
        "es",
        "que",
        "por",
        "para",
        "con",
        "se",
    }
    normal = (texto or "").lower()
    tokens = [token for token in re.findall(r"[a-záéíóúñü0-9%]+", normal) if token not in stop]
    for token in tokens:
        valores[_casilla(token, dim)] += 3.0
        if len(token) >= 5:
            valores[_casilla(token[:5], dim)] += 2.0
    for indice in range(len(tokens) - 1):
        valores[_casilla(tokens[indice] + " " + tokens[indice + 1], dim)] += 4.0
    norma = sum(v * v for v in valores) ** 0.5 or 1.0
    return [v / norma for v in valores]


def _casilla(texto: str, dim: int) -> int:
    digest = sha256(texto.encode("utf-8")).hexdigest()
    return int(digest, 16) % dim


def _url_embeddings(base: str) -> str:
    u = (base or "").strip().rstrip("/")
    if u.endswith("/embeddings"):
        return u
    if u.endswith("/v1"):
        return u + "/embeddings"
    return u + "/v1/embeddings"
