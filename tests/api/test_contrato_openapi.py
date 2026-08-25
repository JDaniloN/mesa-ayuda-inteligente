"""Regresiones para que OpenAPI no se separe del comportamiento probado."""

from src.api.app import create_app
from src.api.repositorio import Repositorio
from src.ia.fachada import FachadaClasificador


def _openapi() -> dict:
    app = create_app(
        repositorio=Repositorio(),
        api_token="test-token",
        clasificador=FachadaClasificador(proveedor=None),
    )
    return app.openapi()


def test_contrato_publica_las_cuatro_operaciones():
    paths = _openapi()["paths"]

    assert set(paths) == {
        "/health",
        "/solicitudes",
        "/solicitudes/{id_solicitud}",
    }
    assert paths["/health"]["get"]["operationId"] == "consultar_salud"
    assert paths["/solicitudes"]["post"]["operationId"] == "crear_solicitud"
    assert paths["/solicitudes"]["get"]["operationId"] == "listar_solicitudes"
    assert (
        paths["/solicitudes/{id_solicitud}"]["get"]["operationId"]
        == "consultar_solicitud"
    )


def test_post_documenta_camino_nuevo_idempotente_y_errores():
    respuestas = _openapi()["paths"]["/solicitudes"]["post"]["responses"]

    assert set(respuestas) == {"200", "201", "401", "409", "422", "500", "503"}
    assert respuestas["201"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/SolicitudSalida"
    }
    assert respuestas["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/RespuestaError"
    }


def test_contrato_declara_bearer_y_error_uniforme():
    componentes = _openapi()["components"]

    assert componentes["securitySchemes"]["HTTPBearer"] == {
        "type": "http",
        "scheme": "bearer",
    }
    assert {"DetalleError", "RespuestaError"} <= set(componentes["schemas"])
    error = componentes["schemas"]["RespuestaError"]
    assert error["required"] == ["error"]


def test_contrato_fija_limites_de_entrada_y_listado():
    contrato = _openapi()
    entrada = contrato["components"]["schemas"]["SolicitudEntrada"]["properties"]
    parametros = contrato["paths"]["/solicitudes"]["get"]["parameters"]
    limite = next(parametro for parametro in parametros if parametro["name"] == "limite")

    assert entrada["asunto"]["minLength"] == 5
    assert entrada["asunto"]["maxLength"] == 200
    assert entrada["descripcion"]["maxLength"] == 4000
    assert limite["schema"]["minimum"] == 1
    assert limite["schema"]["maximum"] == 200
    assert limite["schema"]["default"] == 50


def test_respuestas_documentan_header_de_correlacion():
    paths = _openapi()["paths"]
    respuestas = [
        paths["/health"]["get"]["responses"]["200"],
        paths["/solicitudes"]["post"]["responses"]["201"],
        paths["/solicitudes"]["get"]["responses"]["200"],
        paths["/solicitudes/{id_solicitud}"]["get"]["responses"]["200"],
    ]

    for respuesta in respuestas:
        header = respuesta["headers"]["X-Request-ID"]["schema"]
        assert header == {"type": "string", "format": "uuid"}
