"""Las pruebas nunca llaman a OpenAI ni dependen de secretos locales."""

import os

# El entorno del proceso prevalece sobre `.env` en Configuracion.
os.environ["IA_API_KEY"] = ""
os.environ["IA_API_BASE_URL"] = ""
os.environ["APP_ENV"] = "test"
