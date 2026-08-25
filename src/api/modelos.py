"""Contrato de la API propia.

La entrada copia el mock (asunto, área, solicitante). Categoría y
prioridad salen pendientes hasta el módulo de IA (siguiente ítem).
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class SolicitudEntrada(BaseModel):
    asunto: str = Field(..., min_length=5, max_length=200)
    descripcion: str = Field("", max_length=4000)
    area: str = Field(..., min_length=2, max_length=80)
    solicitante: str = Field(..., min_length=5, max_length=120)
    canal: str = Field("api", max_length=30)


class SolicitudSalida(BaseModel):
    id: str
    asunto: str
    descripcion: str
    area: str
    solicitante: str
    canal: str
    estado: str
    fecha_creacion: str
    categoria: str
    prioridad: str
    origen_clasificacion: str


def ahora_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
