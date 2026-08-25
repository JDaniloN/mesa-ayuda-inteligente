"""Fachada: primero el LLM; si falla, degradado (sin regex de negocio)."""

from __future__ import annotations

import logging
from typing import Optional

from src.configuracion import Configuracion, obtener_configuracion
from src.ia.degradado import clasificar_degradado
from src.ia.modelos import Clasificacion
from src.ia.proveedor_http import ErrorProveedorIA, ProveedorHttp
from src.metricas import RegistroMetricas

log = logging.getLogger("mesa.ia")

REINTENTOS_POR_DEFECTO = 1
ERRORES_TRANSITORIOS = {
    "timeout",
    "conexion",
    "http_408",
    "http_425",
    "http_429",
    "http_500",
    "http_502",
    "http_503",
    "http_504",
}


class FachadaClasificador:
    def __init__(
        self,
        proveedor: Optional[ProveedorHttp] = None,
        reintentos: int = REINTENTOS_POR_DEFECTO,
    ) -> None:
        self._proveedor = proveedor
        self._reintentos = max(0, reintentos)

    @property
    def proveedor_configurado(self) -> bool:
        """Indica configuración sin exponer el adaptador HTTP privado."""

        return self._proveedor is not None

    def close(self) -> None:
        """Libera el cliente HTTP propio al apagar la aplicación."""

        if self._proveedor is not None:
            self._proveedor.close()

    @classmethod
    def desde_configuracion(
        cls,
        configuracion: Configuracion | None = None,
        metricas: RegistroMetricas | None = None,
    ) -> FachadaClasificador:
        config = configuracion or obtener_configuracion()
        url = config.ia_api_base_url.strip()
        clave = config.ia_api_key.get_secret_value().strip()
        modelo = config.ia_model.strip() or "gpt-4o-mini"
        if not url or not clave:
            return cls(proveedor=None)
        return cls(
            proveedor=ProveedorHttp(
                url,
                clave,
                modelo,
                timeout_s=config.ia_timeout,
                metricas=metricas,
            ),
            reintentos=config.ia_reintentos,
        )

    @classmethod
    def desde_entorno(cls) -> FachadaClasificador:
        """Alias compatible; la lectura real está centralizada y tipada."""

        return cls.desde_configuracion()

    def clasificar(self, texto: str) -> Clasificacion:
        if self._proveedor is None:
            log.warning(
                "ia_degradada",
                extra={
                    "event": "ia_degradada",
                    "reason": "configuracion_ausente",
                    "classification_origin": "degradado",
                },
            )
            return clasificar_degradado(texto)
        intentos = self._reintentos + 1
        for i in range(intentos):
            try:
                resultado = self._proveedor.clasificar(texto)
                log.info(
                    "ia_clasificacion_completada",
                    extra={
                        "event": "ia_clasificacion_completada",
                        "classification_origin": resultado.origen,
                        "attempt": i + 1,
                        "max_attempts": intentos,
                    },
                )
                return resultado
            except ErrorProveedorIA as exc:
                log.warning(
                    "ia_intento_fallido",
                    extra={
                        "event": "ia_intento_fallido",
                        "attempt": i + 1,
                        "max_attempts": intentos,
                        "reason": exc.codigo,
                    },
                )
                if exc.codigo not in ERRORES_TRANSITORIOS or i + 1 >= intentos:
                    log.warning(
                        "ia_degradada",
                        extra={
                            "event": "ia_degradada",
                            "reason": exc.codigo,
                            "classification_origin": "degradado",
                        },
                    )
                    return clasificar_degradado(texto)
        return clasificar_degradado(texto)
