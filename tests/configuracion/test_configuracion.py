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


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("mock_timeout", 0),
        ("ia_timeout", -1),
        ("ia_reintentos", 4),
        ("api_port", 70000),
        ("log_level", "VERBOSE"),
    ],
)
def test_configuracion_invalida_falla_claro(campo, valor):
    with pytest.raises(ValidationError):
        Configuracion(_env_file=None, **{campo: valor})


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
