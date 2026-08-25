"""Fachada: primero el LLM; si falla, degradado (sin regex de negocio)."""

from __future__ import annotations

import logging
import os
from typing import Optional

from src.entorno import cargar_entorno
from src.ia.degradado import clasificar_degradado
from src.ia.modelos import Clasificacion
from src.ia.proveedor_http import ErrorProveedorIA, ProveedorHttp

log = logging.getLogger("mesa.ia")

REINTENTOS_POR_DEFECTO = 1
TIMEOUT_POR_DEFECTO = 8.0


class FachadaClasificador:
    def __init__(
        self,
        proveedor: Optional[ProveedorHttp] = None,
        reintentos: int = REINTENTOS_POR_DEFECTO,
    ) -> None:
        self._proveedor = proveedor
        self._reintentos = max(0, reintentos)

    @classmethod
    def desde_entorno(cls) -> FachadaClasificador:
        cargar_entorno()
        url = os.environ.get("IA_API_BASE_URL", "").strip()
        clave = os.environ.get("IA_API_KEY", "").strip()
        modelo = os.environ.get("IA_MODEL", "").strip() or "gpt-4o-mini"
        if not url or not clave:
            return cls(proveedor=None)
        crudo = os.environ.get("IA_TIMEOUT", "").strip()
        timeout_s = float(crudo) if crudo else TIMEOUT_POR_DEFECTO
        reint = os.environ.get("IA_REINTENTOS", "").strip()
        reintentos = int(reint) if reint else REINTENTOS_POR_DEFECTO
        return cls(
            proveedor=ProveedorHttp(url, clave, modelo, timeout_s=timeout_s),
            reintentos=reintentos,
        )

    def clasificar(self, texto: str) -> Clasificacion:
        if self._proveedor is None:
            log.warning(
                "IA degradado: no hay IA_API_BASE_URL o IA_API_KEY en el entorno."
            )
            return clasificar_degradado(texto)
        intentos = self._reintentos + 1
        for i in range(intentos):
            try:
                return self._proveedor.clasificar(texto)
            except ErrorProveedorIA as exc:
                log.warning("IA intento %s/%s falló: %s", i + 1, intentos, exc)
                if i + 1 >= intentos:
                    return clasificar_degradado(texto)
        return clasificar_degradado(texto)
