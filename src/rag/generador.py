"""Generador acotado al contexto recuperado."""

from __future__ import annotations

from typing import Optional

import httpx

from src.rag.modelos import ErrorRag, PuertoGenerador

PROMPT = (
    "Respondes consultas sobre políticas internas de LA FORTUNA. "
    "Responde únicamente con información explícitamente respaldada por los "
    "fragmentos proporcionados. "
    "Si la pregunta contiene varias partes, responde cada una por separado. "
    "No transfieras un plazo, responsable, porcentaje, condición, excepción "
    "o unidad de una cláusula a otra. "
    "Que exista evidencia para una parte no implica que la misma regla aplique "
    "a otra. "
    "Si una parte de la pregunta no está respaldada por los fragmentos, "
    "indícalo expresamente en lugar de inferir o completar la información. "
    "No inventes documentos, secciones, páginas ni plazos. "
    "No cites fuentes que no estén en el contexto."
)


class GeneradorHttp(PuertoGenerador):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        modelo: str,
        timeout_s: float = 8.0,
        http: Optional[httpx.Client] = None,
    ) -> None:
        self._url = _url_chat(base_url)
        self._api_key = api_key
        self._modelo = modelo
        self._propios = http is None
        self._http = http or httpx.Client(timeout=timeout_s)

    def generar(
        self,
        pregunta: str,
        contextos: list[str],
        cobertura: dict | None = None,
    ) -> str:
        piezas = []
        for indice, texto in enumerate(contextos, start=1):
            piezas.append(f"[{indice}]\n{texto}")
        extra = ""
        if cobertura:
            faltantes = [clave for clave, ok in cobertura.items() if not ok]
            if faltantes:
                extra = (
                    "\n\nCobertura de subconsultas: hay partes de la pregunta "
                    "sin hit directo. No completes esas partes por inferencia."
                )
        cuerpo = {
            "model": self._modelo,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Fragmentos:\n"
                        + "\n\n".join(piezas)
                        + extra
                        + "\n\nPregunta:\n"
                        + pregunta.strip()
                    ),
                },
            ],
        }
        try:
            respuesta = self._http.post(
                self._url,
                json=cuerpo,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        except httpx.TimeoutException as exc:
            raise ErrorRag("configuracion", "Timeout al generar la respuesta RAG.") from exc
        except httpx.RequestError as exc:
            raise ErrorRag("configuracion", "No fue posible conectar con el generador.") from exc
        if respuesta.status_code >= 400:
            raise ErrorRag(
                "configuracion",
                f"El generador respondió {respuesta.status_code}.",
            )
        try:
            return respuesta.json()["choices"][0]["message"]["content"].strip()
        except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
            raise ErrorRag("configuracion", "Respuesta del generador inválida.") from exc

    def close(self) -> None:
        if self._propios:
            self._http.close()


class GeneradorFalso(PuertoGenerador):
    def generar(
        self,
        pregunta: str,
        contextos: list[str],
        cobertura: dict | None = None,
    ) -> str:
        if not contextos:
            return ""
        return "Respuesta basada únicamente en los fragmentos recuperados."


def _url_chat(base: str) -> str:
    u = (base or "").strip().rstrip("/")
    if u.endswith("/chat/completions"):
        return u
    if u.endswith("/v1"):
        return u + "/chat/completions"
    return u + "/v1/chat/completions"
