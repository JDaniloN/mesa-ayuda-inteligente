"""Almacén en memoria. La persistencia relacional queda para la etapa 4."""

from __future__ import annotations

import threading
from typing import Optional
from uuid import uuid4

from src.api.modelos import SolicitudEntrada, SolicitudSalida, ahora_iso
from src.ia.modelos import Clasificacion

DEGRADADO = Clasificacion(
    categoria="Sin clasificar",
    prioridad="Media",
    origen="degradado",
)


class Repositorio:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._por_id: dict[str, SolicitudSalida] = {}
        self._idempotencia: dict[str, str] = {}

    def crear(
        self,
        entrada: SolicitudEntrada,
        clave_idempotencia: Optional[str] = None,
        clasificacion: Optional[Clasificacion] = None,
    ) -> tuple[SolicitudSalida, bool]:
        """Devuelve (solicitud, es_nueva). Misma clave y mismo cuerpo reusa."""
        clase = clasificacion or DEGRADADO
        with self._lock:
            if clave_idempotencia:
                existente_id = self._idempotencia.get(clave_idempotencia)
                if existente_id:
                    previa = self._por_id[existente_id]
                    if not _misma_entrada(previa, entrada):
                        raise ClaveIdempotenciaEnUso(
                            "La Idempotency-Key ya se usó con otro cuerpo."
                        )
                    return previa, False
            ident = f"SOL-{uuid4().hex[:8].upper()}"
            salida = SolicitudSalida(
                id=ident,
                asunto=entrada.asunto,
                descripcion=entrada.descripcion,
                area=entrada.area,
                solicitante=entrada.solicitante,
                canal=entrada.canal,
                estado="Abierto",
                fecha_creacion=ahora_iso(),
                categoria=clase.categoria,
                prioridad=clase.prioridad,
                origen_clasificacion=clase.origen,
            )
            self._por_id[ident] = salida
            if clave_idempotencia:
                self._idempotencia[clave_idempotencia] = ident
            return salida, True

    def obtener(self, ident: str) -> Optional[SolicitudSalida]:
        with self._lock:
            return self._por_id.get(ident)

    def listar(
        self,
        area: Optional[str] = None,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        limite: int = 50,
    ) -> list[SolicitudSalida]:
        with self._lock:
            filas = list(self._por_id.values())
        if area:
            filas = [s for s in filas if s.area == area]
        if estado:
            filas = [s for s in filas if s.estado == estado]
        if prioridad:
            filas = [s for s in filas if s.prioridad == prioridad]
        filas.sort(key=lambda s: s.fecha_creacion, reverse=True)
        return filas[:limite]


def _misma_entrada(previa: SolicitudSalida, entrada: SolicitudEntrada) -> bool:
    return (
        previa.asunto == entrada.asunto
        and previa.descripcion == entrada.descripcion
        and previa.area == entrada.area
        and previa.solicitante == entrada.solicitante
        and previa.canal == entrada.canal
    )


class ClaveIdempotenciaEnUso(Exception):
    """La misma clave llegó con un cuerpo distinto."""
