"""Cliente HTTP compatible con /v1/chat/completions (OpenAI y similares)."""

from __future__ import annotations

import json
import re
from typing import Optional

import httpx

from src.ia.catalogo import en_catalogo, prompt_sistema
from src.ia.modelos import Clasificacion
from src.metricas import RegistroMetricas


class ErrorProveedorIA(Exception):
    """Timeout, HTTP de error o JSON que no cumple el catálogo."""

    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(codigo)


class ProveedorHttp:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        modelo: str,
        timeout_s: float = 8.0,
        http: Optional[httpx.Client] = None,
        metricas: RegistroMetricas | None = None,
    ) -> None:
        self._url = _url_chat(base_url)
        self._api_key = api_key
        self._modelo = modelo
        self._timeout_s = timeout_s
        self._propios = http is None
        self._http = http or httpx.Client(timeout=timeout_s)
        self._metricas = metricas

    def close(self) -> None:
        if self._propios:
            self._http.close()

    def clasificar(self, texto: str) -> Clasificacion:
        cuerpo = {
            "model": self._modelo,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": prompt_sistema()},
                {"role": "user", "content": texto.strip() or "(vacío)"},
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
            self._registrar_uso(None)
            raise ErrorProveedorIA("timeout") from exc
        except httpx.RequestError as exc:
            self._registrar_uso(None)
            raise ErrorProveedorIA("conexion") from exc
        try:
            data = respuesta.json()
        except ValueError:
            data = None
        self._registrar_uso(data)
        if respuesta.status_code >= 400:
            raise ErrorProveedorIA(f"http_{respuesta.status_code}")
        try:
            contenido = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ErrorProveedorIA("cuerpo_invalido") from exc
        categoria, prioridad = _parsear_json(contenido)
        if not en_catalogo(categoria, prioridad):
            raise ErrorProveedorIA("fuera_de_catalogo")
        return Clasificacion(
            categoria=categoria, prioridad=prioridad, origen="proveedor"
        )

    def _registrar_uso(self, data: dict | None) -> None:
        if self._metricas is not None:
            usage = data.get("usage") if isinstance(data, dict) else None
            self._metricas.registrar_llamada_ia(
                "clasificacion",
                self._modelo,
                usage,
            )


def _url_chat(base: str) -> str:
    u = (base or "").strip().rstrip("/")
    if u.endswith("/chat/completions"):
        return u
    if u.endswith("/v1"):
        return u + "/chat/completions"
    return u + "/v1/chat/completions"


def _parsear_json(contenido: str) -> tuple[str, str]:
    texto = (contenido or "").strip()
    cerca = re.search(r"\{.*\}", texto, re.DOTALL)
    if cerca:
        texto = cerca.group(0)
    try:
        data = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ErrorProveedorIA("json") from exc
    if not isinstance(data, dict):
        raise ErrorProveedorIA("json")
    if set(data) != {"categoria", "prioridad"}:
        raise ErrorProveedorIA("json")
    categoria = data["categoria"]
    prioridad = data["prioridad"]
    if not isinstance(categoria, str) or not isinstance(prioridad, str):
        raise ErrorProveedorIA("json")
    return categoria.strip(), prioridad.strip()
