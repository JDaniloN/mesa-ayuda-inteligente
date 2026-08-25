"""Parser y chunker sobre los PDF reales, sin modificar materiales/."""

from pathlib import Path

from src.rag.chunker import fragmentar_documento, id_fragmento
from src.rag.extractor import extraer_directorio, extraer_pdf
from src.rag.parser import parsear_documento, tabla_semantica

POLITICAS = Path("materiales/politicas")


def _por_codigo(codigo: str):
    return extraer_pdf(next(POLITICAS.glob(f"{codigo}*.pdf")))


def test_disclaimer_no_es_contenido_recuperable():
    for documento in extraer_directorio(POLITICAS):
        for bloque in parsear_documento(documento):
            assert "Documento sintético" not in bloque.texto
            assert "prueba técnica" not in bloque.texto.lower()


def test_clausula_hereda_titulo_del_padre():
    bloques = parsear_documento(_por_codigo("POL-GTH-01"))
    clause = next(item for item in bloques if item.seccion == "3.1")
    padre = next((item for item in bloques if item.seccion == "3"), None)

    assert clause.seccion_padre == "3"
    assert clause.titulo_seccion == "Solicitud y aprobación"
    assert "quince" in clause.texto.lower()
    assert "calendario" in clause.texto.lower()
    if padre is not None:
        assert padre.titulo_seccion == "Solicitud y aprobación"


def test_causacion_no_mezcla_anticipacion():
    bloques = {item.seccion: item for item in parsear_documento(_por_codigo("POL-GTH-01"))}

    assert "año completo" in bloques["2"].texto.lower()
    assert "calendario" not in bloques["2"].texto.lower()
    assert "anticipación" in bloques["3.1"].texto.lower()


def test_tabla_semantica_no_duplica_filas():
    bloques = {item.seccion: item for item in parsear_documento(_por_codigo("POL-TIC-05"))}
    texto = bloques["4"].texto

    assert texto.lower().count("15 minutos") == 1
    assert "Primera respuesta" in texto
    assert "Solución objetivo" in texto or "Solucion objetivo" in texto


def test_ingesta_ids_deterministas_y_materiales_intactos():
    original = {
        ruta: ruta.stat().st_mtime_ns
        for ruta in POLITICAS.glob("*.pdf")
    }
    documento = _por_codigo("POL-GTH-01")
    primera = fragmentar_documento(documento)
    segunda = fragmentar_documento(documento)

    assert [item.chunk_id for item in primera] == [item.chunk_id for item in segunda]
    assert len({item.chunk_id for item in primera}) == len(primera)
    for ruta, marca in original.items():
        assert ruta.stat().st_mtime_ns == marca


def test_id_cambia_si_cambia_el_texto():
    a = id_fragmento("POL-GTH-01", "3", "2", "texto uno")
    b = id_fragmento("POL-GTH-01", "3", "2", "texto dos")
    assert a != b


def test_tabla_semantica_conserva_clave_valor():
    texto = tabla_semantica(
        [
            ["Prioridad", "Primera respuesta", "Solución objetivo"],
            ["Crítica", "15 minutos", "4 horas"],
        ]
    )
    assert "Prioridad Crítica:" in texto
    assert "- Primera respuesta: 15 minutos" in texto
    assert "- Solución objetivo: 4 horas" in texto
