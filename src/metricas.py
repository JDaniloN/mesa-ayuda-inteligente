"""Métricas agregadas en memoria, sin prompts, cuerpos ni credenciales."""

from __future__ import annotations

import logging
from threading import Lock

log = logging.getLogger("mesa.metricas")


class RegistroMetricas:
    """Acumulador thread-safe para la instancia actual del servicio."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._peticiones = 0
        self._errores = 0
        self._latencia_total_ms = 0.0
        self._latencia_maxima_ms = 0.0
        self._llamadas_ia = 0
        self._tokens_entrada = 0
        self._tokens_salida = 0
        self._tokens_total = 0
        self._uso_no_reportado = 0
        self._por_operacion: dict[str, dict[str, int]] = {}

    def registrar_peticion(self, duracion_ms: float, status_code: int) -> None:
        duracion = max(0.0, float(duracion_ms))
        with self._lock:
            self._peticiones += 1
            self._errores += int(status_code >= 500)
            self._latencia_total_ms += duracion
            self._latencia_maxima_ms = max(self._latencia_maxima_ms, duracion)

    def registrar_llamada_ia(
        self,
        operacion: str,
        modelo: str,
        usage: dict | None,
    ) -> None:
        entrada, salida, total, disponible = _extraer_tokens(usage)
        with self._lock:
            self._llamadas_ia += 1
            self._tokens_entrada += entrada
            self._tokens_salida += salida
            self._tokens_total += total
            self._uso_no_reportado += int(not disponible)
            por_operacion = self._por_operacion.setdefault(
                operacion,
                {
                    "llamadas": 0,
                    "tokens_entrada": 0,
                    "tokens_salida": 0,
                    "tokens_total": 0,
                    "uso_no_reportado": 0,
                },
            )
            por_operacion["llamadas"] += 1
            por_operacion["tokens_entrada"] += entrada
            por_operacion["tokens_salida"] += salida
            por_operacion["tokens_total"] += total
            por_operacion["uso_no_reportado"] += int(not disponible)
        log.info(
            "ia_tokens_consumidos",
            extra={
                "event": "ia_tokens_consumidos",
                "operation": operacion,
                "model": modelo,
                "input_tokens": entrada,
                "output_tokens": salida,
                "total_tokens": total,
                "usage_available": disponible,
            },
        )

    def resumen(self) -> dict:
        with self._lock:
            promedio = (
                self._latencia_total_ms / self._peticiones
                if self._peticiones
                else 0.0
            )
            return {
                "peticiones": {
                    "total": self._peticiones,
                    "errores_5xx": self._errores,
                    "latencia_ms": {
                        "promedio": round(promedio, 2),
                        "maxima": round(self._latencia_maxima_ms, 2),
                        "acumulada": round(self._latencia_total_ms, 2),
                    },
                },
                "ia": {
                    "llamadas": self._llamadas_ia,
                    "tokens_entrada": self._tokens_entrada,
                    "tokens_salida": self._tokens_salida,
                    "tokens_total": self._tokens_total,
                    "uso_no_reportado": self._uso_no_reportado,
                    "por_operacion": {
                        clave: dict(valor)
                        for clave, valor in self._por_operacion.items()
                    },
                },
            }


def _extraer_tokens(usage: dict | None) -> tuple[int, int, int, bool]:
    if not isinstance(usage, dict):
        return 0, 0, 0, False
    entrada = _entero_no_negativo(
        usage.get("prompt_tokens", usage.get("input_tokens", 0))
    )
    salida = _entero_no_negativo(
        usage.get("completion_tokens", usage.get("output_tokens", 0))
    )
    total = _entero_no_negativo(usage.get("total_tokens", entrada + salida))
    return entrada, salida, total, True


def _entero_no_negativo(valor) -> int:
    try:
        return max(0, int(valor))
    except (TypeError, ValueError):
        return 0
