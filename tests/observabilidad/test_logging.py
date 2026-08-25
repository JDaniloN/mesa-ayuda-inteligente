"""Eventos JSON correlacionados y sin secretos ni datos personales."""

import json
import logging
from uuid import UUID

import httpx
from fastapi.testclient import TestClient
import pytest

from src.api.app import create_app
from src.api.repositorio import Repositorio
from src.configuracion import Configuracion
from src.ia.fachada import FachadaClasificador
from src.ia.proveedor_http import ErrorProveedorIA, ProveedorHttp
from src.observabilidad import FormateadorJson


def _config() -> Configuracion:
    return Configuracion(
        _env_file=None,
        app_env="test",
        log_level="INFO",
        ia_api_base_url="",
        ia_api_key="",
    )


def _eventos(texto: str) -> list[dict]:
    return [
        json.loads(linea)
        for linea in texto.splitlines()
        if linea.strip().startswith("{")
    ]


def test_formateador_emite_json_y_descarta_campos_no_permitidos():
    secreto = "sk-no-debe-salir"
    registro = logging.LogRecord(
        name="mesa.prueba",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="evento_prueba",
        args=(),
        exc_info=None,
    )
    registro.event = "evento_prueba"
    registro.reason = "timeout"
    registro.api_key = secreto
    registro.solicitante = "persona@empresa.test"

    datos = json.loads(FormateadorJson("test").format(registro))

    assert datos["event"] == "evento_prueba"
    assert datos["reason"] == "timeout"
    assert secreto not in json.dumps(datos)
    assert "persona@empresa.test" not in json.dumps(datos)


def test_respuesta_y_log_comparten_request_id(capsys):
    cliente = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token="token-prueba",
            clasificador=FachadaClasificador(proveedor=None),
            configuracion=_config(),
        )
    )

    respuesta = cliente.get("/health")
    request_id = respuesta.headers["X-Request-ID"]
    UUID(request_id)
    eventos = _eventos(capsys.readouterr().out)
    evento_http = next(
        evento for evento in eventos if evento["event"] == "http_request_completed"
    )

    assert evento_http["request_id"] == request_id
    assert evento_http["status_code"] == 200
    assert evento_http["method"] == "GET"
    assert evento_http["path"] == "/health"
    assert evento_http["duration_ms"] >= 0


def test_post_no_registra_token_ni_datos_personales(capsys):
    token = "token-super-secreto"
    correo = "persona-secreta@empresa.test"
    descripcion = "detalle privado del incidente"
    cliente = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=token,
            clasificador=FachadaClasificador(proveedor=None),
            configuracion=_config(),
        )
    )

    respuesta = cliente.post(
        "/solicitudes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "asunto": "Falla al abrir el correo",
            "descripcion": descripcion,
            "area": "Aplicaciones",
            "solicitante": correo,
        },
    )

    salida = capsys.readouterr().out
    eventos = _eventos(salida)
    request_id = respuesta.headers["X-Request-ID"]
    assert respuesta.status_code == 201
    assert token not in salida
    assert correo not in salida
    assert descripcion not in salida
    assert {"ia_degradada", "http_request_completed"} <= {
        evento["event"] for evento in eventos
    }
    assert all(evento["request_id"] == request_id for evento in eventos)


def test_error_ia_no_expone_clave_ni_cuerpo_del_proveedor():
    clave = "sk-super-secreta"
    detalle = "respuesta-privada-del-proveedor"

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": detalle})

    proveedor = ProveedorHttp(
        base_url="https://ia.test/v1",
        api_key=clave,
        modelo="demo",
        http=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(ErrorProveedorIA) as capturado:
        proveedor.clasificar("texto privado")

    assert capturado.value.codigo == "http_401"
    assert clave not in str(capturado.value)
    assert detalle not in str(capturado.value)
