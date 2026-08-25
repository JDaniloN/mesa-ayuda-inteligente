import json

import httpx
import pytest

from src.integraciones.cliente import ClienteMock
from src.integraciones.errores import (
    ErrorAutorizacion,
    ErrorLimiteTasa,
    ErrorNoEncontrado,
    ErrorServicio,
    ErrorTimeout,
    ErrorValidacion,
)
from src.integraciones.modelos import SolicitudSalida

SALIDA = {
    "id": "EXT-ABC123",
    "asunto": "Consulta de prueba del cliente mock",
    "descripcion": "",
    "area": "Aplicaciones",
    "solicitante": "usuario001@lafortuna.com.co",
    "canal": "api",
    "estado": "Abierto",
    "fecha_creacion": "2026-01-01T00:00:00+00:00",
}


def _cliente(handler) -> ClienteMock:
    transporte = httpx.MockTransport(handler)
    http = httpx.Client(transport=transporte, base_url="http://test")
    return ClienteMock(base_url="http://test", token="demo", timeout_s=5.0, http=http)


def test_listar_get_200():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/solicitudes"
        assert request.headers["authorization"] == "Bearer demo"
        return httpx.Response(200, json=[SALIDA])

    lista = _cliente(handler).listar()
    assert len(lista) == 1
    assert isinstance(lista[0], SolicitudSalida)
    assert lista[0].id == "EXT-ABC123"


def test_crear_post_201():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/solicitudes"
        assert request.headers["idempotency-key"] == "k-1"
        cuerpo = json.loads(request.content)
        assert cuerpo["asunto"].startswith("Consulta")
        return httpx.Response(201, json={**SALIDA, "asunto": cuerpo["asunto"]})

    creada = _cliente(handler).crear(
        asunto="Consulta de vacaciones",
        area="Aplicaciones",
        solicitante="usuario001@lafortuna.com.co",
        clave_idempotencia="k-1",
    )
    assert creada.id == "EXT-ABC123"
    assert creada.estado == "Abierto"


def test_crear_asunto_corto_no_pega_a_red():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no debe llamar al servicio")

    with pytest.raises(ErrorValidacion, match="contrato"):
        _cliente(handler).crear(
            asunto="Hola",
            area="Aplicaciones",
            solicitante="usuario001@lafortuna.com.co",
        )


def test_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    with pytest.raises(ErrorTimeout, match="5 s"):
        _cliente(handler).listar()


def test_conexion_rechazada():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused", request=request)

    with pytest.raises(ErrorServicio, match="http://test"):
        _cliente(handler).listar()


def test_500_no_reintenta():
    llamadas = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas["n"] += 1
        return httpx.Response(
            500, json={"detail": "Error interno del proveedor. Reintente."}
        )

    with pytest.raises(ErrorServicio):
        _cliente(handler).listar()
    assert llamadas["n"] == 1


def test_429_reintenta_una_vez_si_hay_retry_after():
    llamadas = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas["n"] += 1
        if llamadas["n"] == 1:
            return httpx.Response(
                429,
                json={"detail": "Demasiadas peticiones."},
                headers={"Retry-After": "0"},
            )
        return httpx.Response(200, json=[SALIDA])

    lista = _cliente(handler).listar()
    assert llamadas["n"] == 2
    assert lista[0].id == "EXT-ABC123"


def test_429_sin_exito_al_reintentar_lanza_limite():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            json={"detail": "Demasiadas peticiones."},
            headers={"Retry-After": "0"},
        )

    with pytest.raises(ErrorLimiteTasa):
        _cliente(handler).listar()


def test_401():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Token ausente o inválido."})

    with pytest.raises(ErrorAutorizacion, match="MOCK_TOKEN") as visto:
        _cliente(handler).listar()
    assert "demo" not in str(visto.value)


def test_422_del_proveedor():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "Cuerpo inválido"})

    with pytest.raises(ErrorValidacion, match="Cuerpo inválido"):
        _cliente(handler).crear(
            asunto="Consulta de vacaciones",
            area="Aplicaciones",
            solicitante="usuario001@lafortuna.com.co",
        )


def test_desde_entorno_sin_token(monkeypatch):
    monkeypatch.setenv("MOCK_TOKEN", "")
    with pytest.raises(ErrorAutorizacion, match="MOCK_TOKEN"):
        ClienteMock.desde_entorno()


def test_timeout_entorno_invalido(monkeypatch):
    monkeypatch.setenv("MOCK_TOKEN", "demo")
    monkeypatch.setenv("MOCK_TIMEOUT", "cinco")
    with pytest.raises(ErrorValidacion, match="MOCK_TIMEOUT"):
        ClienteMock.desde_entorno()


def test_obtener_200():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/solicitudes/EXT-ABC123"
        return httpx.Response(200, json=SALIDA)

    una = _cliente(handler).obtener("EXT-ABC123")
    assert una.id == "EXT-ABC123"


def test_obtener_404():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Solicitud no encontrada."})

    with pytest.raises(ErrorNoEncontrado, match="no encontrada"):
        _cliente(handler).obtener("EXT-NOEXISTE")


def test_obtener_id_vacio_no_pega_a_red():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no debe llamar al servicio")

    with pytest.raises(ErrorValidacion, match="id"):
        _cliente(handler).obtener("  ")


def test_429_sin_retry_after_no_reintenta():
    llamadas = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas["n"] += 1
        return httpx.Response(429, json={"detail": "Demasiadas peticiones."})

    with pytest.raises(ErrorLimiteTasa):
        _cliente(handler).listar()
    assert llamadas["n"] == 1


def test_201_con_cuerpo_invalido():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json={"id": "EXT-1"})

    with pytest.raises(ErrorValidacion, match="contrato"):
        _cliente(handler).crear(
            asunto="Consulta de vacaciones",
            area="Aplicaciones",
            solicitante="usuario001@lafortuna.com.co",
        )


def test_200_que_no_es_json():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="no-json")

    with pytest.raises(ErrorValidacion, match="JSON"):
        _cliente(handler).listar()
