"""Logs JSON seguros y correlación de eventos por petición."""

from __future__ import annotations

from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import sys
from typing import Any

_REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="-")

_CAMPOS_SEGUROS = (
    "method",
    "path",
    "status_code",
    "duration_ms",
    "attempt",
    "max_attempts",
    "reason",
    "classification_origin",
    "exception_type",
    "operation",
    "model",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "usage_available",
)


def request_id_actual() -> str:
    return _REQUEST_ID.get()


def establecer_request_id(valor: str):
    return _REQUEST_ID.set(valor)


def restablecer_request_id(token) -> None:
    _REQUEST_ID.reset(token)


class FormateadorJson(logging.Formatter):
    """Serializa solo campos permitidos; nunca cuerpos ni credenciales."""

    def __init__(self, environment: str) -> None:
        super().__init__()
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        evento = getattr(record, "event", None)
        if not evento:
            evento = record.getMessage()
        datos: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": str(evento),
            "request_id": getattr(record, "request_id", request_id_actual()),
            "environment": self.environment,
        }
        for campo in _CAMPOS_SEGUROS:
            if hasattr(record, campo):
                datos[campo] = getattr(record, campo)
        return json.dumps(datos, ensure_ascii=False, default=str)


def configurar_logging(nivel: str, environment: str) -> logging.Logger:
    """Configura una sola salida JSON a stdout para los loggers `mesa.*`."""

    logger = logging.getLogger("mesa")
    logger.setLevel(getattr(logging, nivel.upper(), logging.INFO))
    logger.propagate = False
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FormateadorJson(environment))
    logger.addHandler(handler)
    return logger
