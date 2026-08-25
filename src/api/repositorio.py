"""Almacén en memoria. La persistencia relacional queda para la etapa 4."""

from __future__ import annotations

from contextlib import contextmanager
import threading
from collections.abc import Iterator
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
        self._bloqueos_idempotencia: dict[str, threading.Lock] = {}

    @contextmanager
    def serializar_idempotencia(
        self,
        clave_idempotencia: Optional[str],
    ) -> Iterator[None]:
        """Serializa solo peticiones con la misma clave, incluso durante IA."""

        if not clave_idempotencia:
            yield
            return
        with self._lock:
            bloqueo = self._bloqueos_idempotencia.setdefault(
                clave_idempotencia,
                threading.Lock(),
            )
        with bloqueo:
            yield

    def crear(
        self,
        entrada: SolicitudEntrada,
        clave_idempotencia: Optional[str] = None,
        clasificacion: Optional[Clasificacion] = None,
    ) -> tuple[SolicitudSalida, bool]:
        """Devuelve (solicitud, es_nueva). Misma clave y mismo cuerpo reusa."""
        clase = clasificacion or DEGRADADO
        with self._lock:
            previa = self._resolver_idempotencia(entrada, clave_idempotencia)
            if previa is not None:
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

    def recuperar_idempotente(
        self,
        entrada: SolicitudEntrada,
        clave_idempotencia: Optional[str],
    ) -> Optional[SolicitudSalida]:
        """Recupera o rechaza una clave antes de ejecutar efectos externos."""

        with self._lock:
            return self._resolver_idempotencia(entrada, clave_idempotencia)

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

    def _resolver_idempotencia(
        self,
        entrada: SolicitudEntrada,
        clave_idempotencia: Optional[str],
    ) -> Optional[SolicitudSalida]:
        if not clave_idempotencia:
            return None
        existente_id = self._idempotencia.get(clave_idempotencia)
        if not existente_id:
            return None
        previa = self._por_id[existente_id]
        if not _misma_entrada(previa, entrada):
            raise ClaveIdempotenciaEnUso(
                "La Idempotency-Key ya se usó con otro cuerpo."
            )
        return previa


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
