"""Tres recursos: crear, consultar estado, listar con filtros."""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response

from src.api.auth import exigir_token
from src.api.errores import cuerpo
from src.api.modelos import SolicitudEntrada, SolicitudSalida
from src.api.repositorio import ClaveIdempotenciaEnUso, Repositorio

router = APIRouter(prefix="/solicitudes", dependencies=[Depends(exigir_token)])


def _repo(request: Request) -> Repositorio:
    return request.app.state.repositorio


@router.post("", response_model=SolicitudSalida)
def crear(
    entrada: SolicitudEntrada,
    request: Request,
    response: Response,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    clave = (idempotency_key or "").strip() or None
    texto = f"{entrada.asunto}\n{entrada.descripcion}".strip()
    clasificacion = request.app.state.clasificador.clasificar(texto)
    try:
        salida, nueva = _repo(request).crear(entrada, clave, clasificacion)
    except ClaveIdempotenciaEnUso as exc:
        raise HTTPException(status_code=409, detail=cuerpo("conflicto", str(exc))) from exc
    response.status_code = 201 if nueva else 200
    return salida


@router.get("", response_model=list[SolicitudSalida])
def listar(
    request: Request,
    area: Optional[str] = Query(default=None),
    estado: Optional[str] = Query(default=None),
    prioridad: Optional[str] = Query(default=None),
    limite: int = Query(default=50, ge=1, le=200),
):
    return _repo(request).listar(
        area=area, estado=estado, prioridad=prioridad, limite=limite
    )


@router.get("/{id_solicitud}", response_model=SolicitudSalida)
def obtener(id_solicitud: str, request: Request):
    ident = (id_solicitud or "").strip()
    if not ident:
        raise HTTPException(
            status_code=422,
            detail=cuerpo("validacion", "Falta el id de la solicitud."),
        )
    hallada = _repo(request).obtener(ident)
    if hallada is None:
        raise HTTPException(
            status_code=404,
            detail=cuerpo("no_encontrado", "No se encontró la solicitud."),
        )
    return hallada
