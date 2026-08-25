from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.repositorio import Repositorio
from src.ia.fachada import FachadaClasificador
from src.rag.embeddings import EmbeddingsFalsos
from src.rag.generador import GeneradorFalso
from src.rag.servicio import ServicioPoliticas
from src.rag.vector_store import AlmacenChroma

TOKEN = "test-token"


def _cliente(tmp_path) -> TestClient:
    servicio = ServicioPoliticas(
        almacen=AlmacenChroma(tmp_path / "rag"),
        embeddings=EmbeddingsFalsos(),
        generador=GeneradorFalso(),
        min_score=0.08,
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
