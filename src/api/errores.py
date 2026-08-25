"""Errores de la API propia. Un solo cuerpo para todas las rutas."""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def cuerpo(codigo: str, mensaje: str) -> dict:
    return {"error": {"codigo": codigo, "mensaje": mensaje}}


def respuesta(status: int, codigo: str, mensaje: str) -> JSONResponse:
    return JSONResponse(status_code=status, content=cuerpo(codigo, mensaje))


async def validacion_invalida(_request: Request, exc: RequestValidationError):
    partes = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", ()) if x != "body")
        partes.append(f"{loc}: {err.get('msg', 'inválido')}" if loc else err.get("msg", "inválido"))
    mensaje = "La solicitud no cumple el contrato. " + "; ".join(partes)
    return respuesta(422, "validacion", mensaje)


async def http_excepcion(_request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    codigo = {
        401: "no_autorizado",
        404: "no_encontrado",
        409: "conflicto",
        422: "validacion",
        503: "configuracion",
    }.get(exc.status_code, "error")
    mensaje = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return respuesta(exc.status_code, codigo, mensaje)


async def error_no_controlado(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        return await http_excepcion(request, exc)
    if isinstance(exc, RequestValidationError):
        return await validacion_invalida(request, exc)
    return respuesta(500, "error", "El servicio falló. Intente de nuevo.")
