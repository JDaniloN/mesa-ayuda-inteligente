"""Carga `.env` de la raíz una sola vez.

Pisa variables de la sesión: si no, un `$env:IA_API_KEY` viejo en la
misma terminal gana y el archivo parece no funcionar.
"""

from pathlib import Path

from dotenv import load_dotenv

_RAIZ = Path(__file__).resolve().parent.parent
_cargado = False


def cargar_entorno() -> None:
    global _cargado
    if _cargado:
        return
    load_dotenv(_RAIZ / ".env", override=True)
    _cargado = True
