from concurrent.futures import ThreadPoolExecutor
import json
import threading

from fastapi.testclient import TestClient
import pytest

from src.api.app import create_app
from src.api.repositorio import Repositorio
from src.ia.fachada import FachadaClasificador

TOKEN = "test-token"
CUERPO = {
    "asunto": "No me carga el correo de la sede",
    "descripcion": "Desde ayer",
    "area": "Aplicaciones",
    "solicitante": "usuario001@lafortuna.com.co",
}


def _cliente() -> TestClient:
    return TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=TOKEN,
            clasificador=FachadaClasificador(proveedor=None),
        )
    )


def test_health_no_pide_token():
    r = _cliente().get("/health")
    assert r.status_code == 200
    assert r.json()["estado"] == "operativo"
    assert r.json()["clasificador"] == "sin_clave"


def test_health_aparece_en_openapi():
    r = _cliente().get("/openapi.json")
    assert r.status_code == 200
    assert "/health" in r.json()["paths"]


def test_health_usa_capacidad_publica_del_clasificador():
    from src.ia.modelos import Clasificacion

    class Configurado:
        proveedor_configurado = True

        def clasificar(self, _texto: str) -> Clasificacion:
            return Clasificacion("Sin clasificar", "Media", "degradado")

    cliente = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=TOKEN,
            clasificador=Configurado(),
        )
    )

    assert cliente.get("/health").json()["clasificador"] == "proveedor"


def test_apagado_libera_recursos_del_clasificador():
    from src.ia.modelos import Clasificacion

    class Cerrable:
        proveedor_configurado = False
        cerrado = False

        def clasificar(self, _texto: str) -> Clasificacion:
            return Clasificacion("Sin clasificar", "Media", "degradado")

        def close(self) -> None:
            self.cerrado = True

    clasificador = Cerrable()
    app = create_app(
        repositorio=Repositorio(),
        api_token=TOKEN,
        clasificador=clasificador,
    )

    with TestClient(app) as cliente:
        assert cliente.get("/health").status_code == 200
        assert clasificador.cerrado is False

    assert clasificador.cerrado is True


def test_sin_token_es_401_uniforme():
    r = _cliente().get("/solicitudes")
    assert r.status_code == 401
    assert r.json()["error"]["codigo"] == "no_autorizado"


def test_token_malo_es_401():
    r = _cliente().get(
        "/solicitudes", headers={"Authorization": "Bearer otro"}
    )
    assert r.status_code == 401
    assert "error" in r.json()


def test_sin_api_token_configurado_es_503():
    r = TestClient(create_app(repositorio=Repositorio(), api_token="")).get(
        "/solicitudes", headers={"Authorization": "Bearer x"}
    )
    assert r.status_code == 503
    assert r.json()["error"]["codigo"] == "configuracion"


def test_cors_permite_solo_frontend_local_y_cabeceras_necesarias():
    cliente = _cliente()
    permitida = cliente.options(
        "/solicitudes",
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    externa = cliente.options(
        "/solicitudes",
        headers={
            "Origin": "https://tercero.example",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )

    assert permitida.status_code == 200
    assert permitida.headers["Access-Control-Allow-Origin"] == "http://localhost:4200"
    assert "authorization" in permitida.headers["Access-Control-Allow-Headers"].lower()
    assert "Access-Control-Allow-Credentials" not in permitida.headers
    assert "Access-Control-Allow-Origin" not in externa.headers


def test_crear_201_y_consultar_estado():
    c = _cliente()
    creada = c.post(
        "/solicitudes",
        json=CUERPO,
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert creada.status_code == 201
    cuerpo = creada.json()
    assert cuerpo["estado"] == "Abierto"
    assert cuerpo["origen_clasificacion"] == "degradado"
    assert cuerpo["id"].startswith("SOL-")

    una = c.get(
        f"/solicitudes/{cuerpo['id']}",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert una.status_code == 200
    assert una.json()["id"] == cuerpo["id"]


def test_id_inexistente_es_404_uniforme():
    r = _cliente().get(
        "/solicitudes/SOL-NOEXISTE",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["codigo"] == "no_encontrado"


def test_asunto_corto_es_422_uniforme():
    r = _cliente().post(
        "/solicitudes",
        json={**CUERPO, "asunto": "ab"},
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["codigo"] == "validacion"


def test_listar_filtra_por_area():
    c = _cliente()
    h = {"Authorization": f"Bearer {TOKEN}"}
    c.post("/solicitudes", json=CUERPO, headers=h)
    c.post(
        "/solicitudes",
        json={**CUERPO, "asunto": "Vacaciones de diciembre largo", "area": "Talento Humano"},
        headers=h,
    )
    apps = c.get("/solicitudes", params={"area": "Aplicaciones"}, headers=h)
    assert apps.status_code == 200
    assert len(apps.json()) == 1
    assert apps.json()[0]["area"] == "Aplicaciones"

    todas = c.get("/solicitudes", headers=h)
    assert len(todas.json()) == 2


def test_listar_filtro_sin_match_es_lista_vacia():
    r = _cliente().get(
        "/solicitudes",
        params={"estado": "Cerrado"},
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.parametrize("limite", [0, 201])
def test_limite_fuera_de_rango_es_422(limite):
    r = _cliente().get(
        "/solicitudes",
        params={"limite": limite},
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["codigo"] == "validacion"


def test_idempotencia_misma_clave_no_duplica():
    c = _cliente()
    h = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": "k-1"}
    a = c.post("/solicitudes", json=CUERPO, headers=h)
    b = c.post("/solicitudes", json=CUERPO, headers=h)
    assert a.status_code == 201
    assert b.status_code == 200
    assert a.json()["id"] == b.json()["id"]
    listado = c.get("/solicitudes", headers={"Authorization": f"Bearer {TOKEN}"})
    assert len(listado.json()) == 1


def test_idempotencia_misma_clave_otro_cuerpo_es_409():
    c = _cliente()
    h = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": "k-2"}
    c.post("/solicitudes", json=CUERPO, headers=h)
    r = c.post(
        "/solicitudes",
        json={**CUERPO, "asunto": "Otro asunto distinto ok"},
        headers=h,
    )
    assert r.status_code == 409
    assert r.json()["error"]["codigo"] == "conflicto"


def test_idempotencia_evitaria_repetir_la_clasificacion_externa():
    from src.ia.modelos import Clasificacion

    class Contador:
        llamadas = 0

        def clasificar(self, _texto: str) -> Clasificacion:
            self.llamadas += 1
            return Clasificacion("Aplicaciones", "Media", "proveedor")

    clasificador = Contador()
    c = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=TOKEN,
            clasificador=clasificador,
        )
    )
    h = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": "k-sin-costo"}

    primera = c.post("/solicitudes", json=CUERPO, headers=h)
    repetida = c.post("/solicitudes", json=CUERPO, headers=h)

    assert primera.status_code == 201
    assert repetida.status_code == 200
    assert clasificador.llamadas == 1


def test_idempotencia_concurrente_serializa_la_misma_clave():
    from src.ia.modelos import Clasificacion

    class Lento:
        def __init__(self):
            self.llamadas = 0
            self._lock = threading.Lock()
            self.iniciado = threading.Event()
            self.segunda_llamada = threading.Event()
            self.continuar = threading.Event()

        def clasificar(self, _texto: str) -> Clasificacion:
            with self._lock:
                self.llamadas += 1
                if self.llamadas == 2:
                    self.segunda_llamada.set()
            self.iniciado.set()
            assert self.continuar.wait(timeout=2)
            return Clasificacion("Aplicaciones", "Media", "proveedor")

    clasificador = Lento()
    app = create_app(
        repositorio=Repositorio(),
        api_token=TOKEN,
        clasificador=clasificador,
    )
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Idempotency-Key": "k-concurrente",
    }

    def enviar():
        return TestClient(app).post(
            "/solicitudes",
            json=CUERPO,
            headers=headers,
        )

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        primera = ejecutor.submit(enviar)
        assert clasificador.iniciado.wait(timeout=2)
        segunda = ejecutor.submit(enviar)
        assert clasificador.segunda_llamada.wait(timeout=0.2) is False
        clasificador.continuar.set()
        respuestas = [primera.result(timeout=3), segunda.result(timeout=3)]

    assert sorted(respuesta.status_code for respuesta in respuestas) == [200, 201]
    assert respuestas[0].json()["id"] == respuestas[1].json()["id"]
    assert clasificador.llamadas == 1


def test_listado_filtra_prioridad_y_ordena_mas_reciente_primero():
    from src.ia.modelos import Clasificacion

    class PorContenido:
        def clasificar(self, contexto: str) -> Clasificacion:
            entrada = json.loads(contexto)
            prioridad = "Alta" if "Vacaciones" in entrada["asunto"] else "Media"
            return Clasificacion("Aplicaciones", prioridad, "proveedor")

    c = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=TOKEN,
            clasificador=PorContenido(),
        )
    )
    h = {"Authorization": f"Bearer {TOKEN}"}
    primera = c.post("/solicitudes", json=CUERPO, headers=h).json()
    segunda = c.post(
        "/solicitudes",
        json={**CUERPO, "asunto": "Vacaciones de diciembre largo"},
        headers=h,
    ).json()

    todas = c.get("/solicitudes", headers=h)
    altas = c.get("/solicitudes", params={"prioridad": "Alta"}, headers=h)

    assert [fila["id"] for fila in todas.json()] == [segunda["id"], primera["id"]]
    assert [fila["prioridad"] for fila in altas.json()] == ["Alta"]


def test_error_no_controlado_es_500_generico_y_correlacionado():
    class RepositorioRoto(Repositorio):
        def listar(self, **_filtros):
            raise RuntimeError("detalle interno que no debe exponerse")

    c = TestClient(
        create_app(
            repositorio=RepositorioRoto(),
            api_token=TOKEN,
            clasificador=FachadaClasificador(proveedor=None),
        ),
        raise_server_exceptions=False,
    )

    respuesta = c.get(
        "/solicitudes",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert respuesta.status_code == 500
    assert respuesta.json() == {
        "error": {"codigo": "error", "mensaje": "El servicio falló. Intente de nuevo."}
    }
    assert respuesta.headers["X-Request-ID"]
    assert "detalle interno" not in respuesta.text


def test_post_201_si_el_llm_responde_500():
    """El 500 es del proveedor de IA, no de la mesa: el ticket se crea."""
    import httpx

    from src.ia.fachada import FachadaClasificador
    from src.ia.proveedor_http import ProveedorHttp

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    clasificador = FachadaClasificador(
        proveedor=ProveedorHttp(
            base_url="http://ia.test/v1",
            api_key="sk-test",
            modelo="demo",
            timeout_s=2.0,
            http=httpx.Client(
                transport=httpx.MockTransport(handler),
                base_url="http://ia.test",
            ),
        ),
        reintentos=0,
    )
    c = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=TOKEN,
            clasificador=clasificador,
        )
    )
    r = c.post(
        "/solicitudes",
        json=CUERPO,
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert r.status_code == 201
    assert r.json()["origen_clasificacion"] == "degradado"
    assert r.json()["categoria"] == "Sin clasificar"


def test_post_usa_clasificador_del_puerto():
    from src.ia.modelos import Clasificacion

    class Fijo:
        def clasificar(self, texto: str) -> Clasificacion:
            contexto = json.loads(texto)
            assert contexto == {
                "asunto": "Solicito vacaciones de diciembre",
                "descripcion": "Desde ayer",
            }
            return Clasificacion("Vacaciones", "Alta", "proveedor")

    c = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=TOKEN,
            clasificador=Fijo(),
        )
    )
    r = c.post(
        "/solicitudes",
        json={
            **CUERPO,
            "asunto": "Solicito vacaciones de diciembre",
        },
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert r.status_code == 201
    assert r.json()["categoria"] == "Vacaciones"
    assert r.json()["prioridad"] == "Alta"
    assert r.json()["origen_clasificacion"] == "proveedor"
