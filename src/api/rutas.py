"""Tres recursos: crear, consultar estado, listar con filtros."""

from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    status,
)

from src.api.auth import exigir_token
from src.api.errores import cuerpo
from src.api.modelos import RespuestaError, SolicitudEntrada, SolicitudSalida
from src.api.repositorio import ClaveIdempotenciaEnUso, Repositorio

router = APIRouter(
    prefix="/solicitudes",
    tags=["solicitudes"],
    dependencies=[Depends(exigir_token)],
)

CABECERA_REQUEST_ID = {
    "X-Request-ID": {
        "description": "Identificador UUID para correlacionar respuesta y logs.",
        "schema": {"type": "string", "format": "uuid"},
    }
}


def _error(descripcion: str) -> dict:
    return {
        "model": RespuestaError,
        "description": descripcion,
        "headers": CABECERA_REQUEST_ID,
    }


def _repo(request: Request) -> Repositorio:
    return request.app.state.repositorio


@router.post(
    "",
    response_model=SolicitudSalida,
    status_code=status.HTTP_201_CREATED,
    operation_id="crear_solicitud",
    summary="Crear una solicitud",
    description=(
        "Valida, clasifica y registra una solicitud. Una Idempotency-Key "
        "repetida con el mismo cuerpo devuelve la solicitud existente."
    ),
    responses={
        200: {
            "model": SolicitudSalida,
            "description": "Solicitud existente recuperada por idempotencia.",
            "headers": CABECERA_REQUEST_ID,
        },
        201: {
            "model": SolicitudSalida,
            "description": "Solicitud creada.",
            "headers": CABECERA_REQUEST_ID,
        },
        401: _error("Falta el Bearer o fue rechazado."),
        409: _error("La Idempotency-Key ya se usó con otro cuerpo."),
        422: _error("La entrada no cumple el contrato."),
        500: _error("Fallo inesperado del servicio."),
        503: _error("API_TOKEN no está configurado."),
    },
)
def crear(
    entrada: SolicitudEntrada,
    request: Request,
    response: Response,
    idempotency_key: Optional[str] = Header(
        default=None,
        alias="Idempotency-Key",
        description="Clave opcional para evitar solicitudes duplicadas.",
    ),
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


@router.get(
    "",
    response_model=list[SolicitudSalida],
    operation_id="listar_solicitudes",
    summary="Listar solicitudes",
    description=(
        "Devuelve las solicitudes más recientes. Los filtros son opcionales, "
        "exactos y sensibles a mayúsculas."
    ),
    responses={
        200: {
            "description": "Listado; puede ser una lista vacía.",
            "headers": CABECERA_REQUEST_ID,
        },
        401: _error("Falta el Bearer o fue rechazado."),
        422: _error("El límite está fuera del rango permitido."),
        500: _error("Fallo inesperado del servicio."),
        503: _error("API_TOKEN no está configurado."),
    },
)
def listar(
    request: Request,
    area: Optional[str] = Query(default=None, description="Coincidencia exacta."),
    estado: Optional[str] = Query(default=None, description="Coincidencia exacta."),
    prioridad: Optional[str] = Query(
        default=None,
        description="Crítica, Alta, Media o Baja; coincidencia exacta.",
    ),
    limite: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Máximo de resultados, entre 1 y 200.",
    ),
):
    return _repo(request).listar(
        area=area, estado=estado, prioridad=prioridad, limite=limite
    )


@router.get(
    "/{id_solicitud}",
    response_model=SolicitudSalida,
    operation_id="consultar_solicitud",
    summary="Consultar una solicitud",
    description="Obtiene el estado y la clasificación actuales por identificador.",
    responses={
        200: {
            "description": "Solicitud encontrada.",
            "headers": CABECERA_REQUEST_ID,
        },
        401: _error("Falta el Bearer o fue rechazado."),
        404: _error("No existe una solicitud con ese identificador."),
        500: _error("Fallo inesperado del servicio."),
        503: _error("API_TOKEN no está configurado."),
    },
)
def obtener(
    request: Request,
    id_solicitud: str = Path(description="Identificador con prefijo SOL-."),
):
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
