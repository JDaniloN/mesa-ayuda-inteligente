"""Pruebas de regresión para los tres defectos reportados del legado."""

from datetime import date
from importlib import reload

from src.legacy import legacy_module


def test_s1_filtrar_por_periodo_incluye_ambos_extremos():
    tickets = [
        {"id": "antes", "fecha_creacion": "2025-02-28"},
        {"id": "inicio", "fecha_creacion": "2025-03-01"},
        {"id": "medio", "fecha_creacion": "2025-03-15"},
        {"id": "fin", "fecha_creacion": "2025-03-31"},
        {"id": "despues", "fecha_creacion": "2025-04-01"},
    ]

    resultado = legacy_module.filtrar_por_periodo(
        tickets,
        date(2025, 3, 1),
        date(2025, 3, 31),
    )

    assert [ticket["id"] for ticket in resultado] == ["inicio", "medio", "fin"]


def test_s2_resumir_por_area_no_comparte_datos_entre_llamadas():
    modulo = reload(legacy_module)

    primer_resumen = modulo.resumir_por_area([{"area": "Aplicaciones"}])
    segundo_resumen = modulo.resumir_por_area([{"area": "Contabilidad"}])

    assert primer_resumen == {"Aplicaciones": 1}
    assert segundo_resumen == {"Contabilidad": 1}
    assert primer_resumen is not segundo_resumen


def test_s2_resumir_por_area_conserva_un_acumulador_explicito():
    acumulador = {"Aplicaciones": 2}

    resultado = legacy_module.resumir_por_area(
        [{"area": "Aplicaciones"}, {"area": "Contabilidad"}],
        acumulador,
    )

    assert resultado is acumulador
    assert resultado == {"Aplicaciones": 3, "Contabilidad": 1}


def test_s3_contar_reaperturas_usa_el_hecho_y_no_el_estado_actual():
    tickets = [
        {"estado": "Cerrado", "reaperturas": "2"},
        {"estado": "REABIERTO", "reaperturas": 1},
        {"estado": "reabierto", "reaperturas": ""},
        {"estado": "Abierto", "reaperturas": "0"},
    ]

    assert legacy_module.contar_reaperturas(tickets) == 2


def test_s3_contar_reaperturas_ignora_contadores_desconocidos():
    tickets = [
        {"estado": "reabierto", "reaperturas": None},
        {"estado": "reabierto", "reaperturas": ""},
        {"estado": "reabierto", "reaperturas": "dato-corrupto"},
    ]

    assert legacy_module.contar_reaperturas(tickets) == 0
