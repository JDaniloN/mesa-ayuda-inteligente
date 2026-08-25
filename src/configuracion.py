"""Configuración tipada: entorno del proceso > `.env` > valores seguros."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ = Path(__file__).resolve().parent.parent


class Configuracion(BaseSettings):
    """Contrato único de configuración para la aplicación."""

    model_config = SettingsConfigDict(
        env_file=RAIZ / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_token: SecretStr = SecretStr("")
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)

    mock_url: str = Field(
        default="http://localhost:8080",
        validation_alias=AliasChoices("MOCK_URL", "MOCK_BASE_URL"),
    )
    mock_token: SecretStr = SecretStr("")
    mock_timeout: float = Field(default=5.0, gt=0)

    ia_api_base_url: str = "https://api.openai.com/v1"
    ia_api_key: SecretStr = SecretStr("")
    ia_model: str = "gpt-4o-mini"
    ia_timeout: float = Field(default=8.0, gt=0)
    ia_reintentos: int = Field(default=1, ge=0, le=3)
    ia_embedding_model: str = "text-embedding-3-small"

    # Umbral provisional de abstención RAG; se calibra en el ítem de abstención.
    rag_min_score: float = Field(default=0.22, ge=0.0, le=1.0)
    rag_indice_dir: str = "data/salida/rag"

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Carga una sola configuración para el proceso."""

    return Configuracion()
