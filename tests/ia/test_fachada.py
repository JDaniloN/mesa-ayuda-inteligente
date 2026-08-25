import httpx

from src.configuracion import Configuracion
from src.ia.fachada import FachadaClasificador
from src.ia.proveedor_http import ProveedorHttp


def _http(handler) -> ProveedorHttp:
    return ProveedorHttp(
        base_url="http://ia.test/v1",
        api_key="sk-test",
        modelo="demo",
        timeout_s=2.0,
        http=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="http://ia.test",
        ),
    )


def test_sin_proveedor_es_degradado_sin_regex():
    c = FachadaClasificador(proveedor=None)
    r = c.clasificar("solicito vacaciones urgentes")
    assert r.origen == "degradado"
    assert r.categoria == "Sin clasificar"
    assert r.prioridad == "Media"


def test_llm_feliz_usa_catalogo():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"categoria": "Vacaciones", "prioridad": "Alta"}'
                        }
                    }
                ]
            },
        )

    r = FachadaClasificador(proveedor=_http(handler)).clasificar("quiero vacaciones")
    assert r.origen == "proveedor"
    assert r.categoria == "Vacaciones"
    assert r.prioridad == "Alta"


def test_500_reintenta_y_luego_degrada():
    n = {"hits": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        n["hits"] += 1
        return httpx.Response(500, json={"error": "boom"})

    r = FachadaClasificador(proveedor=_http(handler), reintentos=1).clasificar("x")
    assert n["hits"] == 2
    assert r.origen == "degradado"


def test_json_fuera_de_catalogo_degrada():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": '{"categoria": "Inventado", "prioridad": "Alta"}'}}
                ]
            },
        )

    r = FachadaClasificador(proveedor=_http(handler), reintentos=0).clasificar("x")
    assert r.origen == "degradado"


def test_timeout_degrada():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("slow")

    r = FachadaClasificador(proveedor=_http(handler), reintentos=0).clasificar("x")
    assert r.origen == "degradado"


def test_401_degrada_sin_inventar_categoria():
    n = {"hits": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        n["hits"] += 1
        return httpx.Response(401, json={"error": {"code": "invalid_api_key"}})

    r = FachadaClasificador(proveedor=_http(handler), reintentos=3).clasificar(
        "solicito vacaciones urgentes"
    )
    assert r.origen == "degradado"
    assert r.categoria == "Sin clasificar"
    assert n["hits"] == 1


def test_429_degrada():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"code": "insufficient_quota"}})

    r = FachadaClasificador(proveedor=_http(handler), reintentos=0).clasificar("x")
    assert r.origen == "degradado"


def test_sin_conexion_degrada():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline")

    r = FachadaClasificador(proveedor=_http(handler), reintentos=0).clasificar("x")
    assert r.origen == "degradado"


def test_json_entre_markdown_sigue_siendo_proveedor():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '```json\n{"categoria": "Vacaciones", "prioridad": "Alta"}\n```'
                        }
                    }
                ]
            },
        )

    r = FachadaClasificador(proveedor=_http(handler)).clasificar("vacaciones")
    assert r.origen == "proveedor"
    assert r.categoria == "Vacaciones"


def test_json_invalido_no_se_reintenta_por_ser_error_determinista():
    n = {"hits": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        n["hits"] += 1
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "respuesta inválida"}}]},
        )

    r = FachadaClasificador(
        proveedor=_http(handler),
        reintentos=3,
    ).clasificar("x")

    assert r.origen == "degradado"
    assert n["hits"] == 1


def test_desde_configuracion_expone_estado_publico_del_proveedor():
    sin_clave = Configuracion(
        _env_file=None,
        ia_api_base_url="https://ia.test/v1",
        ia_api_key="",
    )
    con_clave = Configuracion(
        _env_file=None,
        ia_api_base_url="https://ia.test/v1",
        ia_api_key="clave-de-prueba",
    )

    degradado = FachadaClasificador.desde_configuracion(sin_clave)
    proveedor = FachadaClasificador.desde_configuracion(con_clave)

    assert degradado.proveedor_configurado is False
    assert proveedor.proveedor_configurado is True
    proveedor.close()
