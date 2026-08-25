"""Resumen operativo sin exponer prompts, cuerpos ni credenciales."""

from fastapi import APIRouter, Depends, Request

from src.api.auth import exigir_token
from src.api.modelos import MetricasResumen, RespuestaError
from src.api.rutas import CABECERA_REQUEST_ID

router = APIRouter(
    prefix="/metricas",
    tags=["metricas"],
    dependencies=[Depends(exigir_token)],
)


@router.get(
    "/resumen",
    response_model=MetricasResumen,
    operation_id="consultar_metricas",
    summary="Consultar métricas agregadas",
    description=(
        "Resume latencia HTTP y tokens reportados por el proveedor durante "
        "la vida de esta instancia. No incluye prompts ni datos personales."
    ),
    responses={
        200: {
            "description": "Resumen acumulado de la instancia.",
            "headers": CABECERA_REQUEST_ID,
        },
        401: {
            "model": RespuestaError,
            "description": "Falta el Bearer o fue rechazado.",
            "headers": CABECERA_REQUEST_ID,
        },
    },
)
def resumen(request: Request):
    return request.app.state.metricas.resumen()
