"""Catálogo cerrado: las mismas etiquetas que la limpieza del CSV."""

from src.datos.limpiar import CATEGORIAS_VALIDAS, PRIORIDADES_VALIDAS, CATEGORIA_SIN_DATO

PRIORIDAD_POR_DEFECTO = "Media"


def prompt_sistema() -> str:
    cats = ", ".join(sorted(CATEGORIAS_VALIDAS))
    pris = ", ".join(sorted(PRIORIDADES_VALIDAS))
    return (
        "Clasificas solicitudes internas de mesa de ayuda de LA FORTUNA. "
        "Responde SOLO un JSON con las claves categoria y prioridad. "
        f"categoria debe ser exactamente una de: {cats}. "
        f"prioridad debe ser exactamente una de: {pris}. "
        f"Si el texto no encaja, usa categoria {CATEGORIA_SIN_DATO!r} y "
        f"prioridad {PRIORIDAD_POR_DEFECTO!r}. No inventes otras etiquetas. "
        "No expliques nada fuera del JSON."
    )


def en_catalogo(categoria: str, prioridad: str) -> bool:
    return categoria in CATEGORIAS_VALIDAS and prioridad in PRIORIDADES_VALIDAS
