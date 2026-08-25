"""Consulta de políticas internas con citas verificables."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.auth import exigir_token
from src.api.errores import cuerpo
from src.api.modelos import ConsultaPoliticaEntrada, ConsultaPoliticaSalida, RespuestaError
from src.api.rutas import CABECERA_REQUEST_ID
from src.rag.modelos import ErrorRag
from src.rag.servicio import ServicioPoliticas

log = logging.getLogger("mesa.rag")

router = APIRouter(
    prefix="/politicas",
    tags=["politicas"],
    dependencies=[Depends(exigir_token)],
)


def _error(descripcion: str) -> dict:
    return {
        "model": RespuestaError,
        "description": descripcion,
        "headers": CABECERA_REQUEST_ID,
    }


@router.post(
    "/consultar",
    response_model=ConsultaPoliticaSalida,
    operation_id="consultar_politica",
    summary="Consultar políticas internas",
    description=(
        "Recupera fragmentos de las políticas y responde citando documento "
        "y sección. Si no hay evidencia suficiente, se abstiene."
    ),
    responses={
        200: {
            "description": "Respuesta anclada a fragmentos recuperados, o abstención.",
            "headers": CABECERA_REQUEST_ID,
        },
        401: _error("Falta el Bearer o fue rechazado."),
        422: _error("La pregunta o el límite no cumplen el contrato."),
        500: _error("Fallo inesperado del servicio."),
        503: _error("Falta API_TOKEN, embeddings o índice RAG."),
    },
)
def consultar(entrada: ConsultaPoliticaEntrada, request: Request):
    servicio: ServicioPoliticas | None = getattr(
        request.app.state, "consultor_politicas", None
    )
    if servicio is None:
        raise HTTPException(
            status_code=503,
            detail=cuerpo("configuracion", "El consultor de políticas no está disponible."),
        )
    try:
        resultado = servicio.consultar_politica(entrada.pregunta, entrada.limite)
    except ErrorRag as exc:
        log.warning(
            "rag_request_unavailable",
            extra={"event": "rag_request_unavailable", "reason": exc.codigo},
        )
        raise HTTPException(
            status_code=exc.status,
            detail=cuerpo(
                exc.codigo,
                "El servicio de consulta de políticas no está disponible.",
            ),
        ) from exc
    return {
        "respuesta": resultado.respuesta,
        "citas": [
            {
                "documento": cita["documento"],
                "seccion": cita["seccion"],
                "titulo": cita["titulo"],
                "pagina": cita["pagina"],
                "fragmento_id": cita["fragmento_id"],
            }
            for cita in resultado.citas
        ],
    }
