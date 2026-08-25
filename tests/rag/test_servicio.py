"""Ingesta idempotente, índice incompatible, 503 y abstención mínima."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.repositorio import Repositorio
from src.rag.chunker import id_fragmento
from src.rag.embeddings import EmbeddingsFalsos
from src.rag.generador import GeneradorFalso
from src.rag.modelos import MENSAJE_ABSTENCION, ErrorRag, Fragmento
from src.rag.servicio import ServicioPoliticas
from src.rag.vector_store import AlmacenChroma


def _fragmento(texto: str, seccion: str = "1") -> Fragmento:
    chunk_id = id_fragmento("POL-X", "1", seccion, texto)
    return Fragmento(
        chunk_id=chunk_id,
        codigo="POL-X",
        titulo_documento="Demo",
        version="1",
        seccion=seccion,
        seccion_padre="",
        titulo_seccion="Objeto",
        pagina_inicio=1,
        pagina_fin=1,
        texto=texto,
    )


def test_reingesta_con_hash_distinto_elimina_chunk_obsoleto(tmp_path):
    almacen = AlmacenChroma(tmp_path / "rag")
    embeddings = EmbeddingsFalsos()
    viejo = _fragmento("texto original de vacaciones")
    nuevo = _fragmento("texto modificado de vacaciones")
    almacen.ingestar(
        [viejo],
        embeddings.embed([viejo.texto]),
        modelo=embeddings.modelo,
        documents_hash="hash-a",
    )
    assert viejo.chunk_id in almacen.ids()
    almacen.ingestar(
        [nuevo],
        embeddings.embed([nuevo.texto]),
        modelo=embeddings.modelo,
        documents_hash="hash-b",
    )
    ids = almacen.ids()
    assert nuevo.chunk_id in ids
    assert viejo.chunk_id not in ids


def test_misma_hash_no_duplica(tmp_path):
    servicio = ServicioPoliticas(
        almacen=AlmacenChroma(tmp_path / "rag"),
        embeddings=EmbeddingsFalsos(),
        generador=GeneradorFalso(),
        min_score=0.08,
    )
    servicio.ingestar()
    primero = len(servicio._almacen.ids())
    servicio.ingestar()
    assert len(servicio._almacen.ids()) == primero


def test_indice_de_otro_modelo_no_se_reutiliza(tmp_path):
    almacen = AlmacenChroma(tmp_path / "rag")
    original = EmbeddingsFalsos(modelo="modelo-a")
    servicio = ServicioPoliticas(
        almacen=almacen,
        embeddings=original,
        generador=GeneradorFalso(),
        min_score=0.08,
    )
    servicio.ingestar()
    otro = ServicioPoliticas(
        almacen=almacen,
        embeddings=EmbeddingsFalsos(modelo="modelo-b"),
        generador=GeneradorFalso(),
        min_score=0.08,
    )
    with pytest.raises(ErrorRag) as capturado:
        otro.consultar_politica("¿Cuántos días de vacaciones causa un colaborador?")
    assert capturado.value.codigo == "indice_incompatible"


def test_sin_embeddings_falla_controlado():
    servicio = ServicioPoliticas(
        almacen=AlmacenChroma(Path("data/salida/rag-test-no-existe")),
        embeddings=None,
        generador=None,
        min_score=0.22,
    )
    with pytest.raises(ErrorRag) as capturado:
        servicio.consultar_politica("¿Cuántos días de vacaciones causa un colaborador?")
    assert capturado.value.status == 503
    assert capturado.value.codigo == "configuracion"


def test_pregunta_fuera_de_dominio_se_abstiene(tmp_path):
    servicio = ServicioPoliticas(
        almacen=AlmacenChroma(tmp_path / "rag"),
        embeddings=EmbeddingsFalsos(),
        generador=GeneradorFalso(),
        min_score=0.22,
    )
    servicio.ingestar()
    resultado = servicio.consultar_politica("¿Cuál es la capital de Japón?")
    assert resultado.abstuvo is True
    assert resultado.citas == []
    assert resultado.respuesta == MENSAJE_ABSTENCION


def test_http_503_sin_embeddings_ni_indice():
    cliente = TestClient(
        create_app(
            repositorio=Repositorio(),
            api_token="test-token",
            consultor_politicas=ServicioPoliticas(
                almacen=AlmacenChroma(Path("data/salida/rag-ausente")),
                embeddings=None,
                generador=None,
                min_score=0.22,
            ),
        )
    )
    respuesta = cliente.post(
        "/politicas/consultar",
        json={"pregunta": "¿Cuál es el tiempo de un incidente crítico?", "limite": 4},
        headers={"Authorization": "Bearer test-token"},
    )
    assert respuesta.status_code == 503
    assert respuesta.json()["error"]["codigo"] == "configuracion"
