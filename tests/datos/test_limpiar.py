import pandas as pd
import pytest

from src.datos.limpiar import (
    AREA_SIN_DATO,
    CATEGORIA_SIN_DATO,
    ORDEN_PRIORIDAD,
    eliminar_duplicados,
    exportar,
    motivo_rechazo,
    normalizar_canal,
    normalizar_categoria,
    normalizar_estado,
    normalizar_fecha,
    normalizar_prioridad,
    normalizar_reaperturas,
    normalizar_solicitante,
    parsear_fecha,
    resumir_area_prioridad,
    separar_validos,
)


def test_normaliza_iso():
    assert normalizar_fecha("2025-03-08") == "2025-03-08"


def test_normaliza_barra():
    assert normalizar_fecha("03/06/2025") == "2025-06-03"


def test_normaliza_mes_espanol():
    assert normalizar_fecha("20-Ene-2026") == "2026-01-20"


def test_normaliza_mes_ingles():
    assert normalizar_fecha("30-Jun-2025") == "2025-06-30"


def test_vacio_queda_vacio():
    assert normalizar_fecha("") == ""
    assert normalizar_fecha("   ") == ""
    assert parsear_fecha(None) is None


def test_recorta_espacios():
    assert normalizar_fecha("  07/03/2026  ") == "2026-03-07"


def test_fecha_invalida_lanza_error():
    with pytest.raises(ValueError):
        parsear_fecha("32/13/2025")


def test_texto_no_fecha_lanza_error():
    with pytest.raises(ValueError):
        parsear_fecha("ayer")


def test_categoria_unifica_escritura():
    assert normalizar_categoria("SOFTWARE") == "Software"
    assert normalizar_categoria("nómina") == "Nómina"
    assert normalizar_categoria("NOMINA") == "Nómina"
    assert normalizar_categoria("Gestion de accesos") == "Gestión de accesos"
    assert normalizar_categoria("Órdenes de compra") == "Órdenes de compra"
    assert normalizar_categoria("RED") == "Red"


def test_categoria_no_junta_sinonimos():
    assert normalizar_categoria("Acceso") == "Acceso"
    assert normalizar_categoria("accesos") == "Accesos"
    assert normalizar_categoria("equipos") == "Equipos"
    assert normalizar_categoria("hardware") == "Hardware"
    assert normalizar_categoria("incidente") == "Incidente"
    assert normalizar_categoria("Incidentes") == "Incidentes"
    assert normalizar_categoria("Aplicaciones") == "Aplicaciones"
    assert normalizar_categoria("Reportes") == "Reportes"
    assert normalizar_categoria("Otros") == "Otros"
    assert normalizar_categoria("Sin clasificar") == "Sin clasificar"
    assert normalizar_categoria("") == CATEGORIA_SIN_DATO
    assert normalizar_categoria(None) == CATEGORIA_SIN_DATO


def test_prioridad_como_en_esquema():
    assert normalizar_prioridad("ALTA") == "Alta"
    assert normalizar_prioridad("1-Alta") == "Alta"
    assert normalizar_prioridad("2-Media") == "Media"
    assert normalizar_prioridad("3-Baja") == "Baja"
    assert normalizar_prioridad("CRITICA") == "Crítica"
    assert normalizar_prioridad("crítica") == "Crítica"
    assert normalizar_prioridad("") == ""


def test_reaperturas_vacias_son_cero():
    assert normalizar_reaperturas("") == "0"
    assert normalizar_reaperturas("  ") == "0"
    assert normalizar_reaperturas("2") == "2"


def test_solicitante_vacio_es_no_identificado():
    assert normalizar_solicitante("") == "No identificado"
    assert normalizar_solicitante("usuario@lafortuna.com.co") == "usuario@lafortuna.com.co"


def test_estado_unifica_escritura():
    assert normalizar_estado("ABIERTO") == "Abierto"
    assert normalizar_estado("reabierto") == "Reabierto"
    assert normalizar_estado("CERRADO") == "Cerrado"
    assert normalizar_estado("en proceso") == "En proceso"
    assert normalizar_estado("Escalado") == "Escalado"
    assert normalizar_estado("") == ""


def test_canal_unifica_escritura():
    assert normalizar_canal("correo") == "Correo"
    assert normalizar_canal("Telefono") == "Teléfono"
    assert normalizar_canal("TELÉFONO") == "Teléfono"
    assert normalizar_canal("formulario") == "Formulario"
    assert normalizar_canal("Formulario web") == "Formulario web"
    assert normalizar_canal("mesa de ayuda") == "Mesa de ayuda"


def test_elimina_duplicados_por_id():
    df = pd.DataFrame(
        {
            "id": ["TK-1", "TK-1", "TK-2"],
            "categoria": ["Hardware", "Hardware", "Nómina"],
        }
    )
    limpio = eliminar_duplicados(df)
    assert len(limpio) == 2
    assert list(limpio["id"]) == ["TK-1", "TK-2"]


def test_exporta_fechas_normalizadas(tmp_path):
    origen = tmp_path / "entrada.csv"
    origen.write_text(
        "id,fecha_creacion,fecha_cierre,area,categoria,asunto,prioridad,reaperturas\n"
        "TK-00001,20-Ene-2026,03/06/2026,Compras,NOMINA,Pago ,Alta,0\n"
        "TK-00001,20-Ene-2026,03/06/2026,Compras,nomina,Pago,Alta,0\n"
        "TK-00002,2025-03-08,,Calidad,equipos,Teclado,Baja,\n",
        encoding="utf-8",
    )
    limpio = tmp_path / "tickets_limpios.csv"

    exportar(origen=origen, limpio=limpio)

    df = pd.read_csv(limpio, dtype=str, keep_default_na=False)
    assert df.loc[0, "fecha_creacion"] == "2026-01-20"
    assert df.loc[0, "fecha_cierre"] == "2026-06-03"
    assert df.loc[1, "fecha_creacion"] == "2025-03-08"
    assert df.loc[1, "fecha_cierre"] == ""
    assert df.loc[0, "categoria"] == "Nómina"
    assert len(df) == 2
    assert df.loc[1, "categoria"] == "Equipos"
    assert df.loc[0, "asunto"] == "Pago"
    assert origen.read_text(encoding="utf-8").count("TK-00001") == 2
    assert (tmp_path / "resumen_area_prioridad.csv").exists()
    assert (tmp_path / "tickets_rechazados.csv").exists()


def test_rechaza_fecha_creacion_invalida():
    fila = pd.Series(
        {
            "id": "TK-9",
            "fecha_creacion": "ayer",
            "fecha_cierre": "",
            "prioridad": "Alta",
            "reaperturas": "0",
        }
    )
    assert motivo_rechazo(fila) == "fecha_creacion ilegible"


def test_area_vacia_no_se_rechaza():
    fila = pd.Series(
        {
            "id": "TK-9",
            "fecha_creacion": "2025-03-08",
            "fecha_cierre": "",
            "area": "",
            "categoria": "",
            "prioridad": "Media",
            "reaperturas": "0",
        }
    )
    assert motivo_rechazo(fila) is None


def test_rechaza_cierre_antes_de_creacion():
    fila = pd.Series(
        {
            "id": "TK-9",
            "fecha_creacion": "2026-03-08",
            "fecha_cierre": "2025-01-01",
            "prioridad": "Alta",
            "reaperturas": "0",
        }
    )
    assert motivo_rechazo(fila) == "fecha_cierre anterior a fecha_creacion"


def test_rechaza_categoria_desconocida():
    fila = pd.Series(
        {
            "id": "TK-9",
            "fecha_creacion": "2025-03-08",
            "fecha_cierre": "",
            "categoria": "Inventada",
            "prioridad": "Alta",
            "reaperturas": "0",
        }
    )
    assert motivo_rechazo(fila) == "categoria no reconocida"


def test_resumen_marca_sin_area():
    df = pd.DataFrame(
        {
            "area": ["Compras", ""],
            "prioridad": ["Alta", "Alta"],
        }
    )
    resumen = resumir_area_prioridad(df)
    assert AREA_SIN_DATO in set(resumen["area"])
    assert "Compras" in set(resumen["area"])


def test_resumen_ordena_prioridad_por_severidad():
    df = pd.DataFrame(
        {
            "area": ["Compras"] * 4,
            "prioridad": ["Baja", "Crítica", "Media", "Alta"],
        }
    )
    resumen = resumir_area_prioridad(df)
    assert list(resumen["prioridad"]) == ORDEN_PRIORIDAD


def test_exporta_separa_rechazados(tmp_path):
    origen = tmp_path / "entrada.csv"
    origen.write_text(
        "id,fecha_creacion,fecha_cierre,area,categoria,prioridad,reaperturas\n"
        "TK-OK,2025-03-08,,Compras,Nómina,Alta,0\n"
        ",2025-03-08,,Compras,Nómina,Alta,0\n",
        encoding="utf-8",
    )
    limpio = tmp_path / "tickets_limpios.csv"
    exportar(origen=origen, limpio=limpio)
    ok = pd.read_csv(limpio, dtype=str, keep_default_na=False)
    mal = pd.read_csv(tmp_path / "tickets_rechazados.csv", dtype=str, keep_default_na=False)
    assert list(ok["id"]) == ["TK-OK"]
    assert mal.loc[0, "motivo"] == "id vacío"


def test_exporta_fecha_invalida_a_rechazados(tmp_path):
    origen = tmp_path / "entrada.csv"
    origen.write_text(
        "id,fecha_creacion,fecha_cierre,area,categoria,prioridad,reaperturas\n"
        "TK-OK,2025-03-08,,Compras,Nómina,Alta,0\n"
        "TK-MAL,ayer,,Compras,Nómina,Alta,0\n",
        encoding="utf-8",
    )
    limpio = tmp_path / "tickets_limpios.csv"
    exportar(origen=origen, limpio=limpio)
    ok = pd.read_csv(limpio, dtype=str, keep_default_na=False)
    mal = pd.read_csv(tmp_path / "tickets_rechazados.csv", dtype=str, keep_default_na=False)
    assert list(ok["id"]) == ["TK-OK"]
    assert mal.loc[0, "motivo"] == "fecha_creacion ilegible"


def test_exporta_archivo_vacio(tmp_path):
    origen = tmp_path / "vacio.csv"
    origen.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="encabezado"):
        exportar(origen=origen, limpio=tmp_path / "tickets_limpios.csv")


def test_exporta_solo_encabezado(tmp_path):
    origen = tmp_path / "solo_cabecera.csv"
    origen.write_text(
        "id,fecha_creacion,fecha_cierre,area,categoria,prioridad\n",
        encoding="utf-8",
    )
    limpio = tmp_path / "tickets_limpios.csv"
    exportar(origen=origen, limpio=limpio)
    ok = pd.read_csv(limpio, dtype=str, keep_default_na=False)
    mal = pd.read_csv(tmp_path / "tickets_rechazados.csv", dtype=str, keep_default_na=False)
    resumen = pd.read_csv(tmp_path / "resumen_area_prioridad.csv", dtype=str, keep_default_na=False)
    assert ok.empty
    assert mal.empty
    assert list(resumen.columns) == ["area", "prioridad", "tickets"]
    assert resumen.empty


def test_exporta_archivo_inexistente(tmp_path):
    with pytest.raises(ValueError, match="No se encontró"):
        exportar(origen=tmp_path / "no_existe.csv", limpio=tmp_path / "tickets_limpios.csv")


def test_exporta_categoria_vacia_es_sin_clasificar(tmp_path):
    origen = tmp_path / "entrada.csv"
    origen.write_text(
        "id,fecha_creacion,fecha_cierre,area,categoria,prioridad,estado,canal,reaperturas\n"
        "TK-1,2025-03-08,,Compras,,Alta,abierto,correo,0\n",
        encoding="utf-8",
    )
    limpio = tmp_path / "tickets_limpios.csv"
    exportar(origen=origen, limpio=limpio)
    df = pd.read_csv(limpio, dtype=str, keep_default_na=False)
    assert df.loc[0, "categoria"] == CATEGORIA_SIN_DATO
    assert df.loc[0, "estado"] == "Abierto"
    assert df.loc[0, "canal"] == "Correo"
