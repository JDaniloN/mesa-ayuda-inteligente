"""Recuperación híbrida con embeddings fake y Chroma temporal."""

from src.rag.embeddings import EmbeddingsFalsos
from src.rag.generador import GeneradorFalso
from src.rag.servicio import ServicioPoliticas
from src.rag.vector_store import AlmacenChroma


def _servicio(tmp_path, min_score=0.08):
    almacen = AlmacenChroma(tmp_path / "rag")
    servicio = ServicioPoliticas(
        almacen=almacen,
        embeddings=EmbeddingsFalsos(),
        generador=GeneradorFalso(),
        min_score=min_score,
    )
    servicio.ingestar()
    return servicio


def _primera(resultado):
    return (resultado.citas[0]["documento"], resultado.citas[0]["seccion"])


def test_vacaciones_causacion(tmp_path):
    resultado = _servicio(tmp_path).consultar_politica(
        "¿Cuántos días de vacaciones causa un colaborador por cada año completo de servicio?"
    )
    assert _primera(resultado) == ("POL-GTH-01", "2")


def test_vacaciones_anticipacion(tmp_path):
    resultado = _servicio(tmp_path).consultar_politica(
        "¿Con cuánta anticipación debo solicitar mis vacaciones?"
    )
    pares = {
        (cita["documento"], cita["seccion"]) for cita in resultado.citas
    }
    assert ("POL-GTH-01", "3.1") in pares or ("POL-GTH-01", "3") in pares


def test_incidentes_clasificacion(tmp_path):
    resultado = _servicio(tmp_path).consultar_politica(
        "¿Qué condiciones hacen que un incidente sea clasificado como crítico?"
    )
    assert _primera(resultado) == ("POL-TIC-05", "3")


def test_incidentes_tiempos(tmp_path):
    resultado = _servicio(tmp_path).consultar_politica(
        "¿Cuál es el tiempo de primera respuesta y el tiempo objetivo de solución para un incidente crítico?"
    )
    assert _primera(resultado) == ("POL-TIC-05", "4")


def test_citas_salen_de_metadatos_recuperados(tmp_path):
    servicio = _servicio(tmp_path)
    resultado = servicio.consultar_politica(
        "¿Cuál es el tiempo de primera respuesta de un incidente crítico?"
    )
    ids = set(servicio._almacen.ids())
    for cita in resultado.citas:
        assert cita["fragmento_id"] in ids
        assert cita["documento"]
        assert cita["seccion"]
        assert cita["titulo"]
        assert cita["pagina"] >= 1
