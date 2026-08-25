"""Contrato y precedencia de las variables de entorno."""

import pytest
from pydantic import ValidationError

from src.configuracion import Configuracion


def test_entorno_del_proceso_prevalece_sobre_dotenv(monkeypatch, tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "APP_ENV=development\nLOG_LEVEL=INFO\nAPI_TOKEN=token-archivo\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    monkeypatch.setenv("API_TOKEN", "token-sistema")

    config = Configuracion(_env_file=dotenv)

    assert config.app_env == "test"
    assert config.log_level == "ERROR"
    assert config.api_token.get_secret_value() == "token-sistema"


def test_dotenv_provee_valores_si_el_proceso_no_los_define(monkeypatch, tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "API_PORT=8123\nLOG_LEVEL=WARNING\nAPI_TOKEN=token-archivo\n",
        encoding="utf-8",
    )
    for nombre in ("API_PORT", "LOG_LEVEL", "API_TOKEN"):
        monkeypatch.delenv(nombre, raising=False)

    config = Configuracion(_env_file=dotenv)

    assert config.api_port == 8123
    assert config.log_level == "WARNING"
    assert config.api_token.get_secret_value() == "token-archivo"


def test_alias_mock_base_url_conserva_compatibilidad(monkeypatch):
    monkeypatch.delenv("MOCK_URL", raising=False)
    monkeypatch.setenv("MOCK_BASE_URL", "https://mock-alias.test")

    config = Configuracion(_env_file=None)

    assert config.mock_url == "https://mock-alias.test"


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("mock_timeout", 0),
        ("ia_timeout", -1),
        ("ia_reintentos", 4),
        ("api_port", 70000),
        ("log_level", "VERBOSE"),
        ("rag_min_score", 1.5),
    ],
)
def test_configuracion_invalida_falla_claro(campo, valor):
    with pytest.raises(ValidationError):
        Configuracion(_env_file=None, **{campo: valor})


def test_rag_min_score_es_configurable_por_entorno(monkeypatch):
    monkeypatch.setenv("RAG_MIN_SCORE", "0.41")

    config = Configuracion(_env_file=None)

    assert config.rag_min_score == 0.41


def test_secretos_no_aparecen_en_representacion():
    secreto = "valor-que-no-debe-imprimirse"
    config = Configuracion(
        _env_file=None,
        api_token=secreto,
        ia_api_key=secreto,
        mock_token=secreto,
    )

    assert secreto not in repr(config)
    assert config.api_token.get_secret_value() == secreto
