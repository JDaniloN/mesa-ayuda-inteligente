"""Embeddings OpenAI-compatibles; nunca se inventan vectores en ejecución real."""

from __future__ import annotations

from hashlib import sha256
from typing import Optional

import httpx
import re

from src.rag.modelos import ErrorRag, PuertoEmbeddings


class EmbeddingsHttp(PuertoEmbeddings):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        modelo: str,
        timeout_s: float = 8.0,
        http: Optional[httpx.Client] = None,
    ) -> None:
        self.modelo = modelo
        self._url = _url_embeddings(base_url)
        self._api_key = api_key
        self._propios = http is None
        self._http = http or httpx.Client(timeout=timeout_s)

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
            raise ErrorRag("configuracion", "Timeout al generar embeddings.") from exc
        except httpx.RequestError as exc:
            raise ErrorRag("configuracion", "No fue posible conectar con embeddings.") from exc
        if respuesta.status_code >= 400:
            raise ErrorRag(
                "configuracion",
                f"El proveedor de embeddings respondió {respuesta.status_code}.",
            )
        try:
            data = respuesta.json()["data"]
            ordenados = sorted(data, key=lambda item: item["index"])
            return [item["embedding"] for item in ordenados]
        except (KeyError, TypeError, ValueError) as exc:
            raise ErrorRag("configuracion", "Respuesta de embeddings inválida.") from exc

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
