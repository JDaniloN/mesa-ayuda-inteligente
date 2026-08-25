"""API REST propia de la mesa de ayuda (etapa 2).

Tres recursos más /health. La clasificación va por src/ia (puerto),
no por el proveedor HTTP directo.
"""

from datetime import datetime, timezone
import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.errores import error_no_controlado, http_excepcion, validacion_invalida
from src.api.repositorio import Repositorio
from src.api.rutas import router
from src.entorno import cargar_entorno
from src.ia.fachada import FachadaClasificador

cargar_entorno()


def create_app(
    *,
    repositorio: Repositorio | None = None,
    api_token: str | None = None,
    clasificador=None,
) -> FastAPI:
    app = FastAPI(
        title="Mesa de Ayuda Inteligente",
        version="0.2.0",
        description="API propia: crear, consultar y listar solicitudes.",
    )
    app.state.repositorio = repositorio or Repositorio()
    app.state.clasificador = clasificador or FachadaClasificador.desde_entorno()
    if api_token is not None:
        app.state.api_token = api_token
    else:
        app.state.api_token = os.environ.get("API_TOKEN", "").strip()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4200",
            "http://127.0.0.1:4200",
        ],
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["*"],
    )
    app.add_exception_handler(RequestValidationError, validacion_invalida)
    app.add_exception_handler(StarletteHTTPException, http_excepcion)
    app.add_exception_handler(Exception, error_no_controlado)
    app.include_router(router)

    @app.get("/health", summary="Estado del servicio")
    def health():
        tiene = getattr(app.state.clasificador, "_proveedor", None) is not None
        return {
            "estado": "operativo",
            "hora": datetime.now(timezone.utc).isoformat(),
            "clasificador": "proveedor" if tiene else "sin_clave",
        }

    return app


app = create_app()
