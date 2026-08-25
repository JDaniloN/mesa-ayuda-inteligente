"""Descomposición determinista de preguntas compuestas, sin Chroma."""

from src.rag.retriever import descomponer_pregunta


def test_pregunta_simple_no_se_parte():
    partes = descomponer_pregunta(
        "¿Cuántos días de vacaciones causa un colaborador por cada año completo de servicio?"
    )
    assert list(partes) == ["original"]


def test_jefe_inmediato_y_dueno_funcional_no_se_parte():
    partes = descomponer_pregunta(
        "¿Quién aprueba un acceso: el jefe inmediato y el dueño funcional?"
    )
    assert list(partes) == ["original"]


def test_descompone_vacaciones_anticipacion_y_tipo_de_dias():
    pregunta = (
        "Si un colaborador quiere salir a vacaciones, ¿con cuántos días de "
        "anticipación debe solicitarlo y en qué tipo de días se calcula "
        "tanto la solicitud como el periodo de descanso?"
    )
    partes = descomponer_pregunta(pregunta)
    assert "subquery_1" in partes and "subquery_2" in partes
    assert "anticipación" in partes["subquery_1"].lower()
    assert "tipo de días" in partes["subquery_2"].lower() or "tipo de dias" in _sin_tildes(
        partes["subquery_2"]
    )


def test_descompone_cierre_y_reapertura():
    pregunta = (
        "Tras solucionarse un incidente en la mesa de ayuda, ¿cuánto tiempo "
        "tiene el sistema para cerrarlo automáticamente si el usuario no "
        "responde, y cuánto tiempo tiene el usuario para reabrirlo si la "
        "falla vuelve a presentarse?"
    )
    partes = descomponer_pregunta(pregunta)
    juntos = partes["subquery_1"].lower() + partes["subquery_2"].lower()
    assert "cerrarlo" in juntos
    assert "reabrirlo" in juntos


def test_descompone_hurto_reporte_y_denuncia():
    pregunta = (
        "Si a un colaborador le roban su computador portátil de la compañía "
        "en la calle, ¿cuánto tiempo tiene para reportar el suceso a la "
        "empresa y qué plazo tiene para radicar la denuncia ante las autoridades?"
    )
    partes = descomponer_pregunta(pregunta)
    assert "reportar" in partes["subquery_1"].lower()
    assert "denuncia" in partes["subquery_2"].lower()


def _sin_tildes(texto: str) -> str:
    return (
        texto.lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
