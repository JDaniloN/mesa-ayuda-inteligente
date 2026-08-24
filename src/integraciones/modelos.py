"""Contrato de entrada y salida del servicio mock.

Copia el esquema de materiales/servicio_mock/openapi.yaml.
No se importa app.py: el mock es un proceso ajeno, no una librería.
"""

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
