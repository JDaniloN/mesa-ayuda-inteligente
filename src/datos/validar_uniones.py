"""Valida si los id repetidos sostienen las uniones de categoría por asunto.

No modifica el CSV limpio. Primero unifica solo escritura; después mira
si las copias cruzan un par que unimos por asunto.
"""

from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.datos.limpiar import ORIGEN, clave_escritura

SALIDA = Path("data/salida/validacion_uniones_duplicados.csv")

# Etiqueta tras mayúsculas/tildes, sin juntar sinónimos.
ESCRITURA = {
    "acceso": "Acceso",
    "accesos": "Accesos",
    "gestion de accesos": "Gestión de accesos",
    "aplicaciones": "Aplicaciones",
    "software": "Software",
    "equipos": "Equipos",
    "hardware": "Hardware",
    "red": "Red",
    "conectividad": "Conectividad",
    "informes": "Informes",
    "reportes": "Reportes",
    "compras": "Compras",
    "ordenes de compra": "Órdenes de compra",
    "incidente": "Incidente",
    "incidentes": "Incidentes",
    "otros": "Otros",
    "sin clasificar": "Sin clasificar",
    "capacitacion": "Capacitación",
    "nomina": "Nómina",
    "vacaciones": "Vacaciones",
    "viaticos": "Viáticos",
}

# Uniones que aplicamos por asunto. Otros y Sin clasificar no entran.
UNIONES = {
    "Accesos": frozenset({"Acceso", "Accesos", "Gestión de accesos"}),
    "Software": frozenset({"Software", "Aplicaciones"}),
    "Hardware": frozenset({"Hardware", "Equipos"}),
    "Conectividad": frozenset({"Conectividad", "Red"}),
    "Informes": frozenset({"Informes", "Reportes"}),
    "Compras": frozenset({"Compras", "Órdenes de compra"}),
    "Incidentes": frozenset({"Incidente", "Incidentes"}),
}

ETIQUETA_A_UNION = {
    etiqueta: nombre
    for nombre, miembros in UNIONES.items()
    for etiqueta in miembros
}


def etiqueta_escritura(valor: str) -> str:
    texto = (valor or "").strip()
    if not texto:
        return ""
    return ESCRITURA.get(clave_escritura(texto), texto)


def grupo(etiqueta: str) -> str:
    if not etiqueta:
        return "(vacío)"
    return ETIQUETA_A_UNION.get(etiqueta, etiqueta)


def clasificar_id(etiquetas: list[str]) -> str:
    distintas = {e for e in etiquetas}
    grupos = {grupo(e) for e in etiquetas}
    if len(distintas) == 1:
        return "iguales"
    if len(grupos) == 1:
        return "corrobora_union"
    return "no_corrobora"


def validar(origen: Path = ORIGEN) -> pd.DataFrame:
    df = pd.read_csv(origen, dtype=str, keep_default_na=False)
    filas = []
    for tid, bloque in df.groupby("id"):
        if len(bloque) < 2:
            continue
        crudas = [c.strip() for c in bloque["categoria"].tolist()]
        escritas = [etiqueta_escritura(c) for c in crudas]
        resultado = clasificar_id(escritas)
        filas.append(
            {
                "id": tid,
                "copias": len(bloque),
                "categorias_originales": " | ".join(crudas),
                "despues_de_escritura": " | ".join(escritas),
                "grupos_union": " | ".join(grupo(e) for e in escritas),
                "resultado": resultado,
            }
        )
    return pd.DataFrame(filas).sort_values("id")


if __name__ == "__main__":
    reporte = validar()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    reporte.to_csv(SALIDA, index=False, encoding="utf-8")

    conteo = reporte["resultado"].value_counts()
    print(f"ids duplicados: {len(reporte)}")
    print(f"iguales (no aportan a la union): {int(conteo.get('iguales', 0))}")
    print(f"corroboran union por asunto: {int(conteo.get('corrobora_union', 0))}")
    print(f"no corroboran: {int(conteo.get('no_corrobora', 0))}")
    print()

    for resultado, titulo in (
        ("corrobora_union", "CORROBORAN"),
        ("no_corrobora", "NO CORROBORAN"),
        ("iguales", "IGUALES (solo copia o escritura)"),
    ):
        bloque = reporte[reporte["resultado"] == resultado]
        print(f"=== {titulo} ({len(bloque)}) ===")
        if bloque.empty:
            print("(ninguno)")
        else:
            for fila in bloque.itertuples(index=False):
                print(f"{fila.id}  {fila.categorias_originales}  ->  {fila.despues_de_escritura}")
        print()
    print(f"Detalle: {SALIDA}")
