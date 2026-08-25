"""Latencia HTTP y tokens se agregan sin guardar contenido sensible."""

import httpx
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.repositorio import Repositorio
from src.ia.fachada import FachadaClasificador
from src.ia.proveedor_http import ProveedorHttp
from src.metricas import RegistroMetricas
from src.rag.embeddings import EmbeddingsHttp


def test_registro_agrega_latencia_y_tokens_por_operacion():
    registro = RegistroMetricas()
    registro.registrar_peticion(10.0, 200)
    registro.registrar_peticion(30.0, 503)
    registro.registrar_llamada_ia(
        "generacion_rag",
        "modelo-prueba",
        {"prompt_tokens": 8, "completion_tokens": 2, "total_tokens": 10},
    )
    registro.registrar_llamada_ia("embeddings", "modelo-prueba", None)

    resumen = registro.resumen()
    assert resumen["peticiones"] == {
        "total": 2,
        "errores_5xx": 1,
        "latencia_ms": {
            "promedio": 20.0,
            "maxima": 30.0,
            "acumulada": 40.0,
        },
    }
    assert resumen["ia"]["llamadas"] == 2
    assert resumen["ia"]["tokens_total"] == 10
    assert resumen["ia"]["uso_no_reportado"] == 1


def test_clientes_http_registran_usage_del_proveedor():
    registro = RegistroMetricas()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/embeddings"):
            return httpx.Response(
                200,
                json={
                    "data": [{"index": 0, "embedding": [1.0, 0.0]}],
                    "usage": {"prompt_tokens": 4, "total_tokens": 4},
                },
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"categoria":"Aplicaciones","prioridad":"Alta"}'
                            )
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 7,
                    "completion_tokens": 3,
                    "total_tokens": 10,
                },
            },
        )

    http = httpx.Client(transport=httpx.MockTransport(handler))
    embeddings = EmbeddingsHttp(
        "https://ia.test/v1",
        "clave",
        "embedding-demo",
        http=http,
        metricas=registro,
    )
    proveedor = ProveedorHttp(
        "https://ia.test/v1",
        "clave",
        "chat-demo",
        http=http,
        metricas=registro,
    )

    assert embeddings.embed(["texto"]) == [[1.0, 0.0]]
    assert proveedor.clasificar("texto").origen == "proveedor"
    por_operacion = registro.resumen()["ia"]["por_operacion"]
    assert por_operacion["embeddings"]["tokens_total"] == 4
    assert por_operacion["clasificacion"]["tokens_total"] == 10
    http.close()


def test_endpoint_metricas_es_autenticado_y_resume_peticiones():
    registro = RegistroMetricas()
    cliente = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token="token-prueba",
            clasificador=FachadaClasificador(proveedor=None),
            metricas=registro,
        )
    )

    assert cliente.get("/health").status_code == 200
    sin_token = cliente.get("/metricas/resumen")
    respuesta = cliente.get(
        "/metricas/resumen",
        headers={"Authorization": "Bearer token-prueba"},
    )

    assert sin_token.status_code == 401
    assert respuesta.status_code == 200
    assert respuesta.json()["peticiones"]["total"] == 2
    assert set(respuesta.json()["ia"]) == {
        "llamadas",
        "tokens_entrada",
        "tokens_salida",
        "tokens_total",
        "uso_no_reportado",
        "por_operacion",
    }
