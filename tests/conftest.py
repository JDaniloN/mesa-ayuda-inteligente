"""Las pruebas no llaman a OpenAI ni dependen del `.env` de desarrollo.

Se carga `.env` y luego se vacían las claves de IA. Así `override=True`
no dispara llamadas reales durante pytest.
"""

import os

from src.entorno import cargar_entorno

cargar_entorno()
os.environ["IA_API_KEY"] = ""
os.environ["IA_API_BASE_URL"] = ""
