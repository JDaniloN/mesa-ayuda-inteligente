"""Ejecuta las tres consultas contra una copia en memoria del esquema.

Imprime todas las filas y escribe CSV en data/salida/ (la consola
parte líneas largas; el CSV no). No modifica esquema.sql.
"""

import csv
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESQUEMA = RAIZ / "materiales" / "datos" / "esquema.sql"
SALIDA = RAIZ / "data" / "salida"
CONSULTAS = (
    RAIZ / "sql" / "01_agregacion_por_area.sql",
    RAIZ / "sql" / "02_join_tres_tablas.sql",
    RAIZ / "sql" / "03_tickets_reabiertos.sql",
)


def _cargar() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(ESQUEMA.read_text(encoding="utf-8"))
    return con


def _filas_a_csv(destino: Path, filas: list[sqlite3.Row]) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    cols = list(filas[0].keys()) if filas else []
    with destino.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        if cols:
            w.writerow(cols)
            for fila in filas:
                w.writerow("" if fila[c] is None else fila[c] for c in cols)


def _imprimir(titulo: str, filas: list[sqlite3.Row], csv_path: Path) -> None:
    print(f"=== {titulo} ({len(filas)} filas) ===")
    if not filas:
        print("(sin filas)")
        print()
        return
    cols = list(filas[0].keys())
    print(" | ".join(cols))
    for fila in filas:
        print(" | ".join("" if fila[c] is None else str(fila[c]) for c in cols))
    print(f"CSV completo: {csv_path}")
    print()


def main() -> int:
    if not ESQUEMA.is_file():
        print(f"No se encontró el esquema: {ESQUEMA}")
        return 1
    con = _cargar()
    for ruta in CONSULTAS:
        filas = list(con.execute(ruta.read_text(encoding="utf-8")))
        csv_path = SALIDA / f"consulta_{ruta.stem}.csv"
        _filas_a_csv(csv_path, filas)
        _imprimir(ruta.name, filas, csv_path)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
