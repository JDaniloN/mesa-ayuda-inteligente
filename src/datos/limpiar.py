"""Limpieza del histórico de tickets.

Lee y escribe con pandas. Las fechas usan reglas explícitas
(no to_datetime a ciegas). No modifica el CSV original de materiales/.

Categorías: catálogo de escritura (mayúsculas y tildes). No se unen
sinónimos; las copias por id no cruzan esos pares. Vacío → Sin clasificar.
"""

import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import pandas as pd

ORIGEN = Path("materiales/datos/tickets_historicos.csv")
LIMPIO = Path("data/salida/tickets_limpios.csv")
RECHAZADOS = Path("data/salida/tickets_rechazados.csv")
RESUMEN = Path("data/salida/resumen_area_prioridad.csv")
COLUMNAS_FECHA = ("fecha_creacion", "fecha_cierre")
PRIORIDADES_VALIDAS = {"Alta", "Media", "Baja", "Crítica"}
ORDEN_PRIORIDAD = ["Crítica", "Alta", "Media", "Baja"]
AREA_SIN_DATO = "Sin área"
CATEGORIA_SIN_DATO = "Sin clasificar"

# Catálogo de escritura. Alternativa descartada: unir Acceso/Accesos/
# Gestión de accesos (y pares similares). Las 39 ids repetidas no cruzan
# esos pares; esquema.sql tampoco cubre Vacaciones, Capacitación ni Compras.
CATEGORIAS_CANONICAS = {
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
CATEGORIAS_VALIDAS = set(CATEGORIAS_CANONICAS.values())

# Mismo catálogo que esquema.sql: Alta, Media, Baja, Crítica.
PRIORIDADES_CANONICAS = {
    "alta": "Alta",
    "1-alta": "Alta",
    "media": "Media",
    "2-media": "Media",
    "baja": "Baja",
    "3-baja": "Baja",
    "critica": "Crítica",
}

ESTADOS_CANONICOS = {
    "abierto": "Abierto",
    "cerrado": "Cerrado",
    "reabierto": "Reabierto",
    "escalado": "Escalado",
    "en proceso": "En proceso",
}
ESTADOS_VALIDOS = set(ESTADOS_CANONICOS.values())

CANALES_CANONICOS = {
    "correo": "Correo",
    "telefono": "Teléfono",
    "formulario": "Formulario",
    "formulario web": "Formulario web",
    "mesa de ayuda": "Mesa de ayuda",
}
CANALES_VALIDOS = set(CANALES_CANONICOS.values())

MESES = {
    "ene": 1,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
    "dec": 12,
}


def parsear_fecha(valor: Optional[str]) -> Optional[date]:
    """Convierte un valor del CSV a date.

    Vacío o None devuelve None. Un valor presente e ilegible lanza ValueError.
    """
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None

    parsed = _parsear_iso(texto) or _parsear_barra(texto) or _parsear_mes(texto)
    if parsed is None:
        raise ValueError(f"Fecha no reconocida: {valor!r}")
    return parsed


def normalizar_fecha(valor: Optional[str]) -> str:
    """Devuelve YYYY-MM-DD, o cadena vacía si el valor viene vacío."""
    parsed = parsear_fecha(valor)
    if parsed is None:
        return ""
    return parsed.isoformat()


def _parsear_iso(texto: str) -> Optional[date]:
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        return None


def _parsear_barra(texto: str) -> Optional[date]:
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        return None


def _parsear_mes(texto: str) -> Optional[date]:
    partes = texto.split("-")
    if len(partes) != 3:
        return None
    dia_txt, mes_txt, anio_txt = partes
    mes = MESES.get(mes_txt.lower())
    if mes is None:
        return None
    try:
        return date(int(anio_txt), mes, int(dia_txt))
    except ValueError:
        return None


def _sin_tildes(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


def clave_escritura(valor: Optional[str]) -> str:
    return _sin_tildes((valor or "").strip().lower())


def normalizar_categoria(valor: Optional[str]) -> str:
    """Unifica mayúsculas y tildes. Vacío → Sin clasificar."""
    if valor is None:
        return CATEGORIA_SIN_DATO
    texto = str(valor).strip()
    if not texto:
        return CATEGORIA_SIN_DATO
    return CATEGORIAS_CANONICAS.get(clave_escritura(texto), texto)


def normalizar_prioridad(valor: Optional[str]) -> str:
    """Deja Alta, Media, Baja o Crítica, como en esquema.sql."""
    if valor is None:
        return ""
    texto = str(valor).strip()
    if not texto:
        return ""
    return PRIORIDADES_CANONICAS.get(clave_escritura(texto), texto)


def normalizar_reaperturas(valor: Optional[str]) -> str:
    """Vacío pasa a 0. El resto se deja como dígito."""
    if valor is None:
        return "0"
    texto = str(valor).strip()
    if not texto:
        return "0"
    return texto


def normalizar_solicitante(valor: Optional[str]) -> str:
    """Vacío pasa a No identificado."""
    if valor is None:
        return "No identificado"
    texto = str(valor).strip()
    if not texto:
        return "No identificado"
    return texto


def normalizar_estado(valor: Optional[str]) -> str:
    """Unifica mayúsculas. Vacío se queda vacío."""
    if valor is None:
        return ""
    texto = str(valor).strip()
    if not texto:
        return ""
    return ESTADOS_CANONICOS.get(clave_escritura(texto), texto)


def normalizar_canal(valor: Optional[str]) -> str:
    """Unifica mayúsculas y tildes. No junta formulario con Formulario web."""
    if valor is None:
        return ""
    texto = str(valor).strip()
    if not texto:
        return ""
    return CANALES_CANONICOS.get(clave_escritura(texto), texto)


def aplicar_fecha(valor: Optional[str]) -> str:
    """Normaliza o deja el texto si es ilegible, para validar después."""
    try:
        return normalizar_fecha(valor)
    except ValueError:
        return ("" if valor is None else str(valor)).strip()


def fecha_es_ilegible(valor: Optional[str]) -> bool:
    texto = "" if valor is None else str(valor).strip()
    if not texto:
        return False
    try:
        parsear_fecha(texto)
    except ValueError:
        return True
    return False


def _fecha_o_none(valor: Optional[str]) -> Optional[date]:
    texto = "" if valor is None else str(valor).strip()
    if not texto or fecha_es_ilegible(texto):
        return None
    return parsear_fecha(texto)


def motivo_rechazo(fila: pd.Series) -> Optional[str]:
    """None si el registro es válido. Área vacía no rechaza."""
    if not str(fila.get("id", "")).strip():
        return "id vacío"
    if fecha_es_ilegible(fila.get("fecha_creacion")):
        return "fecha_creacion ilegible"
    if not str(fila.get("fecha_creacion", "")).strip():
        return "fecha_creacion vacía"
    if fecha_es_ilegible(fila.get("fecha_cierre")):
        return "fecha_cierre ilegible"
    creacion = _fecha_o_none(fila.get("fecha_creacion"))
    cierre = _fecha_o_none(fila.get("fecha_cierre"))
    if creacion is not None and cierre is not None and cierre < creacion:
        return "fecha_cierre anterior a fecha_creacion"
    if "prioridad" in fila.index:
        if str(fila.get("prioridad", "")).strip() not in PRIORIDADES_VALIDAS:
            return "prioridad no reconocida"
    if "categoria" in fila.index:
        categoria = str(fila.get("categoria", "")).strip()
        if categoria and categoria not in CATEGORIAS_VALIDAS:
            return "categoria no reconocida"
    if "estado" in fila.index:
        estado = str(fila.get("estado", "")).strip()
        if estado and estado not in ESTADOS_VALIDOS:
            return "estado no reconocido"
    if "canal" in fila.index:
        canal = str(fila.get("canal", "")).strip()
        if canal and canal not in CANALES_VALIDOS:
            return "canal no reconocido"
    if "reaperturas" in fila.index:
        reaps = str(fila.get("reaperturas", "")).strip()
        if not reaps.isdigit():
            return "reaperturas no numérica"
    return None


def separar_validos(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    motivos = df.apply(motivo_rechazo, axis=1)
    validos = df.loc[motivos.isna()].copy().reset_index(drop=True)
    rechazados = df.loc[motivos.notna()].copy()
    if not rechazados.empty:
        rechazados.insert(0, "motivo", motivos.loc[motivos.notna()].to_list())
    rechazados = rechazados.reset_index(drop=True)
    return validos, rechazados


def resumir_area_prioridad(df: pd.DataFrame) -> pd.DataFrame:
    """Conteo de tickets por área y prioridad. Área vacía → Sin área."""
    if df.empty:
        return pd.DataFrame(columns=["area", "prioridad", "tickets"])
    tmp = df.copy()
    tmp["area"] = tmp["area"].replace("", AREA_SIN_DATO)
    tmp["prioridad"] = pd.Categorical(
        tmp["prioridad"], categories=ORDEN_PRIORIDAD, ordered=True
    )
    return (
        tmp.groupby(["area", "prioridad"], dropna=False, observed=True)
        .size()
        .reset_index(name="tickets")
        .sort_values(["area", "prioridad"])
        .reset_index(drop=True)
    )


def recortar_textos(df: pd.DataFrame) -> pd.DataFrame:
    """Quita espacios al inicio y al final de todas las columnas de texto."""
    salida = df.copy()
    for col in salida.columns:
        salida[col] = salida[col].map(lambda v: v.strip() if isinstance(v, str) else v)
    return salida


def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Deja una fila por id. Las copias son el mismo ticket."""
    if "id" not in df.columns:
        return df
    return df.drop_duplicates(subset=["id"], keep="first").reset_index(drop=True)


def exportar(
    origen: Path = ORIGEN,
    limpio: Path = LIMPIO,
    rechazados: Optional[Path] = None,
    resumen: Optional[Path] = None,
) -> None:
    limpio.parent.mkdir(parents=True, exist_ok=True)
    if rechazados is None:
        rechazados = limpio.parent / RECHAZADOS.name
    if resumen is None:
        resumen = limpio.parent / RESUMEN.name

    try:
        df = pd.read_csv(origen, dtype=str, keep_default_na=False, encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"No se encontró el CSV: {origen}") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError("El CSV no tiene encabezado") from exc
    if df.empty and not list(df.columns):
        raise ValueError("El CSV no tiene encabezado")

    df = recortar_textos(df)
    for col in COLUMNAS_FECHA:
        if col in df.columns:
            df[col] = df[col].map(aplicar_fecha)
    if "categoria" in df.columns:
        df["categoria"] = df["categoria"].map(normalizar_categoria)
    if "prioridad" in df.columns:
        df["prioridad"] = df["prioridad"].map(normalizar_prioridad)
    if "estado" in df.columns:
        df["estado"] = df["estado"].map(normalizar_estado)
    if "canal" in df.columns:
        df["canal"] = df["canal"].map(normalizar_canal)
    if "reaperturas" in df.columns:
        df["reaperturas"] = df["reaperturas"].map(normalizar_reaperturas)
    if "solicitante" in df.columns:
        df["solicitante"] = df["solicitante"].map(normalizar_solicitante)
    df = eliminar_duplicados(df)

    validos, invalidos = separar_validos(df)
    validos.to_csv(limpio, index=False, encoding="utf-8")
    invalidos.to_csv(rechazados, index=False, encoding="utf-8")
    resumir_area_prioridad(validos).to_csv(resumen, index=False, encoding="utf-8")


if __name__ == "__main__":
    exportar()
    print(f"Original (no se toca): {ORIGEN}")
    print(f"Limpio: {LIMPIO}")
    print(f"Rechazados: {RECHAZADOS}")
    print(f"Resumen: {RESUMEN}")
