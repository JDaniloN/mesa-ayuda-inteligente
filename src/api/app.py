"""API REST propia de la mesa de ayuda.

Solicitudes, salud y consulta de políticas. La clasificación va por src/ia
(puerto), no por el proveedor HTTP directo. El RAG vive en src/rag.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.errores import error_no_controlado, http_excepcion, validacion_invalida
from src.api.modelos import EstadoSalud, RespuestaError
from src.api.repositorio import Repositorio
from src.api.rutas import CABECERA_REQUEST_ID, router
from src.api.rutas_politicas import router as router_politicas
from src.configuracion import Configuracion, obtener_configuracion
from src.ia.fachada import FachadaClasificador
from src.ia.puerto import PuertoClasificador
from src.rag.servicio import ServicioPoliticas
from src.observabilidad import (
    configurar_logging,
    establecer_request_id,
    restablecer_request_id,
)

log = logging.getLogger("mesa.api")


def create_app(
    *,
    repositorio: Repositorio | None = None,
    api_token: str | None = None,
    clasificador: PuertoClasificador | None = None,
    consultor_politicas: ServicioPoliticas | None = None,
    configuracion: Configuracion | None = None,
) -> FastAPI:
    config = configuracion or obtener_configuracion()
    configurar_logging(config.log_level, config.app_env)
    clasificador_real = (
        clasificador
        if clasificador is not None
        else FachadaClasificador.desde_configuracion(config)
    )
    consultor_real = (
        consultor_politicas
        if consultor_politicas is not None
        else ServicioPoliticas.desde_configuracion(config)
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            cerrar = getattr(clasificador_real, "close", None)
            if callable(cerrar):
                cerrar()
            cerrar_rag = getattr(consultor_real, "close", None)
            if callable(cerrar_rag):
                cerrar_rag()

    app = FastAPI(
        title="Mesa de Ayuda Inteligente",
        version="0.2.0",
        description=(
            "API interna para crear, consultar y listar solicitudes de soporte. "
            "La clasificación usa un proveedor de IA con modo degradado. "
            "Las políticas internas se consultan con RAG y citas verificables."
        ),
        lifespan=lifespan,
    )
    app.state.configuracion = config
    app.state.repositorio = repositorio or Repositorio()
    app.state.clasificador = clasificador_real
    app.state.consultor_politicas = consultor_real
    if api_token is not None:
        app.state.api_token = api_token
    else:
        app.state.api_token = config.api_token.get_secret_value().strip()

    @app.middleware("http")
    async def registrar_peticion(request, call_next):
        request_id = str(uuid4())
        token_contexto = establecer_request_id(request_id)
        inicio = perf_counter()
        try:
            response = await call_next(request)
            duracion_ms = round((perf_counter() - inicio) * 1000, 2)
            response.headers["X-Request-ID"] = request_id
            nivel = (
                logging.ERROR
                if response.status_code >= 500
                else logging.WARNING
                if response.status_code >= 400
                else logging.INFO
            )
            log.log(
                nivel,
                "http_request_completed",
                extra={
                    "event": "http_request_completed",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duracion_ms,
                },
            )
            return response
        except Exception as exc:
            log.error(
                "http_request_failed",
                extra={
                    "event": "http_request_failed",
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round((perf_counter() - inicio) * 1000, 2),
                    "exception_type": type(exc).__name__,
                },
            )
            response = await error_no_controlado(request, exc)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            restablecer_request_id(token_contexto)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4200",
            "http://127.0.0.1:4200",
        ],
        allow_credentials=False,
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        allow_methods=["GET", "POST"],
        expose_headers=["X-Request-ID"],
    )
    app.add_exception_handler(RequestValidationError, validacion_invalida)
    app.add_exception_handler(StarletteHTTPException, http_excepcion)
    app.add_exception_handler(Exception, error_no_controlado)
    app.include_router(router)
    app.include_router(router_politicas)

    @app.get(
        "/health",
        response_model=EstadoSalud,
        operation_id="consultar_salud",
        summary="Estado del servicio",
        description=(
            "Indica si el proceso está operativo y si arrancó con proveedor "
            "de clasificación configurado. No requiere autenticación."
        ),
        responses={
            200: {
                "description": "Estado del proceso y del clasificador.",
                "headers": CABECERA_REQUEST_ID,
            },
            500: {
                "model": RespuestaError,
                "description": "Fallo inesperado del servicio.",
                "headers": CABECERA_REQUEST_ID,
            },
        },
    )
    def health():
        tiene = bool(
            getattr(app.state.clasificador, "proveedor_configurado", False)
        )
        return {
            "estado": "operativo",
            "hora": datetime.now(timezone.utc).isoformat(),
            "clasificador": "proveedor" if tiene else "sin_clave",
        }

    return app


app = create_app()
