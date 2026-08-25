"""Modo degradado mínimo: no regex todavía.

Si el proveedor no responde, no inventamos categoría. Dejamos
Sin clasificar / Media y lo marcamos degradado. Después de ver el
LLM decidimos si hace falta un regex más fino.
"""

from src.datos.limpiar import CATEGORIA_SIN_DATO
from src.ia.catalogo import PRIORIDAD_POR_DEFECTO
from src.ia.modelos import Clasificacion


def clasificar_degradado(_texto: str = "") -> Clasificacion:
    return Clasificacion(
        categoria=CATEGORIA_SIN_DATO,
        prioridad=PRIORIDAD_POR_DEFECTO,
        origen="degradado",
    )
