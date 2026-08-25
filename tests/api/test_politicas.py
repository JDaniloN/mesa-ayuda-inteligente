from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.repositorio import Repositorio
from src.ia.fachada import FachadaClasificador
from src.rag.embeddings import EmbeddingsFalsos
from src.rag.generador import GeneradorFalso
from src.rag.modelos import ErrorRag
from src.rag.servicio import ServicioPoliticas
from src.rag.vector_store import AlmacenChroma

TOKEN = "test-token"


def _cliente(tmp_path, min_score: float = 0.08) -> TestClient:
    servicio = ServicioPoliticas(
        almacen=AlmacenChroma(tmp_path / "rag"),
        embeddings=EmbeddingsFalsos(),
        generador=GeneradorFalso(),
        min_score=min_score,
    )
    servicio.ingestar()
    return TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=TOKEN,
            clasificador=FachadaClasificador(proveedor=None),
            consultor_politicas=servicio,
        )
    )


def test_consultar_politica_200_con_citas(tmp_path):
    respuesta = _cliente(tmp_path).post(
        "/politicas/consultar",
        json={
            "pregunta": "¿Cuál es el tiempo de primera respuesta de un incidente crítico?",
            "limite": 4,
        },
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    cuerpo = respuesta.json()
    assert respuesta.status_code == 200
    assert cuerpo["respuesta"]
    assert cuerpo["citas"]
    cita = cuerpo["citas"][0]
    assert {"documento", "seccion", "titulo", "pagina", "fragmento_id"} <= set(cita)


def test_consultar_politica_exige_bearer(tmp_path):
    respuesta = _cliente(tmp_path).post(
        "/politicas/consultar",
        json={"pregunta": "¿Cuántos días de vacaciones causa un colaborador?"},
    )
    assert respuesta.status_code == 401


def test_pregunta_corta_es_422(tmp_path):
    respuesta = _cliente(tmp_path).post(
        "/politicas/consultar",
        json={"pregunta": "hola"},
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert respuesta.status_code == 422


def test_http_se_abstiene_sin_evidencia_documental(tmp_path):
    respuesta = _cliente(tmp_path, min_score=0.22).post(
        "/politicas/consultar",
        json={"pregunta": "¿Cuál es la capital de Japón?"},
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "respuesta": (
            "No encontré información suficiente en las políticas proporcionadas "
            "para responder la pregunta."
        ),
        "citas": [],
    }


def test_error_rag_no_expone_detalle_del_proveedor():
    class ConsultorRoto:
        def consultar_politica(self, _pregunta, _limite):
            raise ErrorRag(
                "configuracion",
                "El proveedor privado respondió HTTP 401.",
            )

    cliente = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token=TOKEN,
            clasificador=FachadaClasificador(proveedor=None),
            consultor_politicas=ConsultorRoto(),
        )
    )
    respuesta = cliente.post(
        "/politicas/consultar",
        json={"pregunta": "¿Cuál es la política de vacaciones?"},
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert respuesta.status_code == 503
    assert respuesta.json()["error"] == {
        "codigo": "configuracion",
        "mensaje": "El servicio de consulta de políticas no está disponible.",
    }
    assert "401" not in respuesta.text
