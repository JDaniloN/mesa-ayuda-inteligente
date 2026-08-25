"""Las tres consultas sobre una copia en memoria de esquema.sql.

El enunciado pide tres funciones y un borde. CSV y mock ya los cubren;
aquí se fija el SQL: 8 / 120 / 36, y dos bordes que el dataset feliz
no muestra (área sin tickets; reapertura sin paso en el log).
"""

import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ESQUEMA = RAIZ / "materiales" / "datos" / "esquema.sql"
SQL = RAIZ / "sql"


def _conectar() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(ESQUEMA.read_text(encoding="utf-8"))
    return con


def _consultar(con: sqlite3.Connection, archivo: str) -> list[sqlite3.Row]:
    return list(con.execute((SQL / archivo).read_text(encoding="utf-8")))


def test_agregacion_una_fila_por_area():
    con = _conectar()
    filas = _consultar(con, "01_agregacion_por_area.sql")
    con.close()
    assert len(filas) == 8
    assert sum(f["tickets"] for f in filas) == 120


def test_agregacion_area_sin_tickets_no_desaparece():
    con = _conectar()
    con.execute(
        "INSERT INTO areas VALUES (99, 'Área sin carga', 'Sede Extra', NULL)"
    )
    filas = _consultar(con, "01_agregacion_por_area.sql")
    con.close()
    por_nombre = {f["area"]: f for f in filas}
    assert len(filas) == 9
    vacia = por_nombre["Área sin carga"]
    assert vacia["tickets"] == 0
    assert vacia["no_cerrados"] == 0
    assert vacia["reaperturas_promedio"] == 0


def test_join_tres_tablas_todos_los_tickets():
    con = _conectar()
    filas = _consultar(con, "02_join_tres_tablas.sql")
    con.close()
    assert len(filas) == 120
    assert all(f["solicitante"] and f["area"] for f in filas)


def test_reabiertos_son_el_hecho_no_el_estado():
    con = _conectar()
    filas = _consultar(con, "03_tickets_reabiertos.sql")
    en_estado = con.execute(
        "SELECT COUNT(*) FROM tickets WHERE estado = 'Reabierto'"
    ).fetchone()[0]
    con.close()
    assert len(filas) == 36
    assert en_estado == 28
    assert sum(1 for f in filas if f["estado"] == "Reabierto") == 28


def test_reabiertos_sin_log_igual_salen():
    con = _conectar()
    filas = _consultar(con, "03_tickets_reabiertos.sql")
    con.close()
    sin_fecha = [f for f in filas if f["ultima_reapertura"] is None]
    assert len(sin_fecha) == 8
    assert all(f["reaperturas"] > 0 for f in sin_fecha)
    assert all(f["estado"] != "Reabierto" for f in sin_fecha)
