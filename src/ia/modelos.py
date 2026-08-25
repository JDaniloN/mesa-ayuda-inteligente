"""Salida del clasificador. origen: proveedor | degradado."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Clasificacion:
    categoria: str
    prioridad: str
    origen: str
