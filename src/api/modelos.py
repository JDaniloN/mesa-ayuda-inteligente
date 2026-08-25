"""Contrato de la API propia.

La entrada describe la solicitud del colaborador. Categoría y prioridad
las asigna el clasificador desacoplado o su modo degradado.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SolicitudEntrada(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asunto": "No puedo ingresar al correo corporativo",
                "descripcion": "El acceso falla desde esta mañana.",
                "area": "Aplicaciones",
                "solicitante": "persona@lafortuna.com.co",
                "canal": "api",
            }
        }
    )

    asunto: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Resumen del problema o solicitud.",
    )
    descripcion: str = Field(
        "",
        max_length=4000,
        description="Contexto adicional; puede quedar vacío.",
    )
    area: str = Field(
        ...,
        min_length=2,
        max_length=80,
        description="Área responsable o relacionada con la solicitud.",
    )
    solicitante: str = Field(
        ...,
        min_length=5,
        max_length=120,
        description="Identificador o correo del colaborador.",
    )
    canal: str = Field(
        "api",
        max_length=30,
        description="Canal por el que se recibió la solicitud.",
    )


class SolicitudSalida(BaseModel):
    id: str = Field(description="Identificador generado, con prefijo SOL-.")
    asunto: str
    descripcion: str
    area: str
    solicitante: str
    canal: str
    estado: Literal["Abierto"]
    fecha_creacion: str = Field(description="Fecha UTC en formato ISO 8601.")
    categoria: str = Field(description="Categoría del catálogo cerrado.")
    prioridad: Literal["Crítica", "Alta", "Media", "Baja"]
    origen_clasificacion: Literal["proveedor", "degradado"]


class DetalleError(BaseModel):
    codigo: str = Field(examples=["no_encontrado"])
    mensaje: str = Field(examples=["No se encontró la solicitud."])


class RespuestaError(BaseModel):
    error: DetalleError


class EstadoSalud(BaseModel):
    estado: Literal["operativo"]
    hora: datetime
    clasificador: Literal["proveedor", "sin_clave"]


def ahora_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
